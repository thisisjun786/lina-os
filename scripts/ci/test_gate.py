import json

from test_support import RepositoryCase


class GateTests(RepositoryCase):
    def gate(self, needs=None, **overrides):
        env = {"NEEDS_JSON": json.dumps(needs if needs is not None else {
            "contracts": {"result": "success", "outputs": {}},
            "security": {"result": "success", "outputs": {}}}),
            "EXPECTED_RELEASE": "false", "BASE_REF": "dev", "HEAD_REF": "feature/demo",
            "BASE_REPO": "example/project", "HEAD_REPO": "example/project",
            "BASE_REPO_ID": "100", "HEAD_REPO_ID": "100"}
        return self.cli("gate", env=env | overrides)

    def test_development_and_release_success(self):
        self.passes(self.gate(), "dev-gate: passed")
        self.passes(self.gate(EXPECTED_RELEASE="true", BASE_REF="main", HEAD_REF="dev"),
                    "release-gate: passed")

    def test_failed_cancelled_skipped_unknown_missing_results(self):
        for result in ("failure", "cancelled", "skipped", "unknown", None):
            for job in ("contracts", "security"):
                with self.subTest(result=result, job=job):
                    needs = {"contracts": {"result": "success"}, "security": {"result": "success"}}
                    needs[job] = {} if result is None else {"result": result}
                    self.fails(self.gate(needs), f"{job} must succeed")

    def test_missing_extra_malformed_needs(self):
        for value, message in (("{", "valid JSON"), ("[]", "needs must be an object"),
                               ("{}", "exactly contracts and security"),
                               ('{"contracts":{},"security":{},"extra":{}}', "exactly contracts and security"),
                               ('{"contracts":null,"security":{}}', "contracts must be an object"),
                               ('{"contracts":{},"contracts":{},"security":{}}', "valid JSON")):
            with self.subTest(value=value):
                self.fails(self.gate(NEEDS_JSON=value), message)

    def test_release_source_and_mode_fail_closed(self):
        for change, message in (({"HEAD_REF": "feature"}, "same-repository dev head"),
                                ({"HEAD_REPO": "fork/project"}, "same-repository dev head"),
                                ({"HEAD_REPO_ID": "200"}, "same-repository dev head"),
                                ({"HEAD_REPO_ID": ""}, "HEAD_REPO_ID is required"),
                                ({"EXPECTED_RELEASE": "false"}, "release mode does not match"),
                                ({"EXPECTED_RELEASE": "yes"}, "EXPECTED_RELEASE must be")):
            with self.subTest(change=change):
                release = {"EXPECTED_RELEASE": "true", "BASE_REF": "main", "HEAD_REF": "dev"}
                self.fails(self.gate(**(release | change)), message)
