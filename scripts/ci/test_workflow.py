import copy
import json

from test_support import RepositoryCase


class WorkflowTests(RepositoryCase):
    def setUp(self):
        super().setUp()
        self.workflow = {
            "name": "Fixture", "on": {"pull_request": {"types": ["opened", "reopened", "synchronize", "edited"]}},
            "permissions": {"contents": "read"}, "jobs": {},
            "concurrency": {"group": "lina-os-ci-${{ github.event.pull_request.number }}", "cancel-in-progress": True},
        }
        for name in ("contracts", "security", "dev-gate", "release-gate"):
            job = {"runs-on": "ubuntu-24.04", "timeout-minutes": 5, "steps": [{
                "uses": "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
                "with": {"persist-credentials": False, "fetch-depth": 0 if name == "security" else 1}}]}
            if name.endswith("gate"):
                operator = "==" if name == "release-gate" else "!="
                job["if"] = f"always() && github.base_ref {operator} 'main'"
                job["needs"] = ["contracts", "security"]
                job["steps"].append({"run": "python3 scripts/ci/gate.py"})
            elif name == "contracts":
                job["steps"] += [{"run": command} for command in (
                    "python3 -m unittest discover -s scripts/ci -p 'test_*.py'",
                    "python3 scripts/ci/contracts.py", "python3 scripts/ci/tools.py actionlint",
                    "python3 scripts/ci/public_refs.py")]
            else:
                job["steps"] += [{"run": "python3 scripts/ci/privacy.py --history"},
                                 {"run": "python3 scripts/ci/tools.py secrets"}]
            self.workflow["jobs"][name] = job
        self.save()

    def save(self):
        self.write(".github/workflows/ci.yml", json.dumps(self.workflow))

    def test_workflow_shape(self):
        self.passes(self.cli("contracts"), "contracts: passed")

    def test_workflow_filters_permissions_pin_candidate_timeout_and_gate(self):
        mutations = (
            (lambda w: w["on"].update({"push": {}}), "pull_request events only"),
            (lambda w: w["on"]["pull_request"].update({"paths": ["docs/**"]}), "pull_request events only"),
            (lambda w: w["permissions"].update({"contents": "write"}), "permissions"),
            (lambda w: w["jobs"]["contracts"]["steps"][0].update({"uses": "actions/checkout@v4"}), "reviewed SHA"),
            (lambda w: w["jobs"]["contracts"]["steps"][0]["with"].update({"ref": "dev"}), "merge candidate"),
            (lambda w: w["jobs"]["contracts"].update({"timeout-minutes": 600}), "timeout"),
            (lambda w: w["jobs"]["security"].update({"needs": ["contracts"]}), "independently"),
            (lambda w: w["jobs"]["release-gate"].update({"if": "success()"}), "always aggregate"),
            (lambda w: w["jobs"]["dev-gate"]["steps"].append({"run": "python3 -m unittest"}), "only aggregate"),
        )
        for mutate, message in mutations:
            saved = copy.deepcopy(self.workflow)
            with self.subTest(message=message):
                mutate(self.workflow)
                self.save()
                self.fails(self.cli("contracts"), message)
            self.workflow = saved

    def test_form_invalid_json_and_shape(self):
        for content, message in (("name: unsupported syntax", "invalid JSON"),
                                 ('{"name":"Bug","description":"Report","body":{}}', "body must be an array")):
            self.write(".github/ISSUE_TEMPLATE/bug.yml", content)
            self.fails(self.cli("contracts"), message)

    def test_source_commands_step_failures_and_concurrency_cannot_be_weakened(self):
        mutations = (
            (lambda w: w["concurrency"].update({"cancel-in-progress": False}), "PR concurrency"),
            (lambda w: w["jobs"]["security"]["steps"][1].update({"continue-on-error": True}), "step cannot skip or suppress"),
            (lambda w: w["jobs"]["security"]["steps"][1].update({"if": "false"}), "step cannot skip or suppress"),
            (lambda w: w["jobs"]["security"]["steps"][1].update({"run": "python3 scripts/ci/privacy.py"}), "required source commands"),
            (lambda w: w["jobs"]["contracts"]["steps"].pop(), "required source commands"),
        )
        for mutate, message in mutations:
            saved = copy.deepcopy(self.workflow)
            with self.subTest(message=message):
                mutate(self.workflow)
                self.save()
                self.fails(self.cli("contracts"), message)
            self.workflow = saved
