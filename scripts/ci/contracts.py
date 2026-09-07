"""Validate the design manifest, local documents and JSON-formatted YAML."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from repository import parse_json, parser, read_source, record, require, run, source_files

PUBLIC_REPOSITORY = "https://github.com/thisisjun786/lina"
CHECKOUT = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
SOURCE_COMMANDS = {
    "contracts": ["python3 -m unittest discover -s scripts/ci -p 'test_*.py'",
                  "python3 scripts/ci/contracts.py", "python3 scripts/ci/tools.py actionlint",
                  "python3 scripts/ci/public_refs.py"],
    "security": ["python3 scripts/ci/privacy.py --history", "python3 scripts/ci/tools.py secrets"],
}
REQUIRED_DOCS = ("README.md", "AGENTS.md", "POLICY.md", "CONTRIBUTING.md", "SECURITY.md",
                 "LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "docs/CI.md",
                 "docs/PUBLICATION.md", "docs/PLANNING.md", "docs/ACCEPTANCE.md")


def nonempty(value: object, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be a nonempty string")


def validate_modules(root: Path) -> dict:
    manifest = record(parse_json(read_source(root, Path("modules.json")), "modules.json"), "modules.json")
    require(set(manifest) == {"schemaVersion", "status", "productRepository", "productSourceRevision",
                             "dataHome", "profiles", "modules", "isolation"}, "modules.json keys are invalid")
    require(type(manifest["schemaVersion"]) is int and manifest["schemaVersion"] == 1,
            "schemaVersion must be 1")
    require(manifest["status"] == "design", "status must be design")
    require(manifest["productRepository"] == PUBLIC_REPOSITORY, "productRepository must be the public Lina repository")
    revision = manifest["productSourceRevision"]
    require(isinstance(revision, str) and bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
            "productSourceRevision must be a 40-character source revision")
    nonempty(manifest["dataHome"], "dataHome")
    modules = record(manifest["modules"], "modules")
    require(bool(modules), "modules cannot be empty")
    for name, value in modules.items():
        require(bool(re.fullmatch(r"[a-z][a-z0-9-]*", name)), "invalid module name")
        module = record(value, f"module {name}")
        require({"owner", "status"} <= set(module) <= {"owner", "status", "foundation", "independentLifecycle"},
                "module keys are invalid")
        require(module["owner"] in ("lina", "lina-os", "external"), "invalid module owner")
        require(module["status"] in ("source-pinned", "planned", "onboarding-required", "development-tool"),
                "invalid module status")
        if "foundation" in module:
            nonempty(module["foundation"], "foundation")
        if "independentLifecycle" in module:
            require(module["independentLifecycle"] is True, "independentLifecycle must be true")
    profiles = record(manifest["profiles"], "profiles")
    require(set(profiles) == {"native", "dedicated-computer", "os"}, "profile keys are invalid")
    for name, members in profiles.items():
        require(isinstance(members, list) and bool(members), f"profile {name} must be a nonempty array")
        require(all(isinstance(member, str) for member in members), "profile members must be strings")
        require(len(set(members)) == len(members), "duplicate profile module")
        require(all(member in modules for member in members), f"undefined profile module in {name}")
    isolation = record(manifest["isolation"], "isolation")
    require(set(isolation) == {"direct", "task-container", "runtime-container"}, "isolation keys are invalid")
    for value in isolation.values():
        nonempty(value, "isolation description")
    return manifest


def markdown_prose(text: str) -> str:
    return re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)


def links(text: str) -> list[str]:
    prose = re.sub(r"`[^`\n]+`", "", markdown_prose(text))
    inline = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", prose)
    references = re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", prose)
    autolinks = re.findall(r"<(https?://[^>]+)>", prose)
    return [value.strip("<>") for value in inline + references + autolinks]


def anchors(text: str) -> set[str]:
    result, counts = set(), {}
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", markdown_prose(text)):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        result.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    result.update(re.findall(r'<a\s+(?:name|id)=[\'"]([^\'"]+)', text))
    return result


def validate_links(root: Path, files: list[Path]) -> None:
    available = set(files)
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        for link in links(read_source(root, path)):
            url = urlsplit(link)
            if url.scheme or url.netloc:
                require(url.scheme in {"https", "http", "mailto"}, f"unsupported local link scheme in {path}")
                continue
            if url.path.startswith("/"):
                target = root / unquote(url.path).lstrip("/")
            else:
                target = root / path.parent / unquote(url.path)
            if not url.path:
                target = root / path
            resolved = target.resolve()
            require(resolved.is_relative_to(root), f"local link escapes repository in {path}")
            relative = resolved.relative_to(root)
            require(relative in available or (target.is_dir() and any(relative in p.parents for p in files)),
                    f"broken local link in {path}")
            if url.fragment and target.suffix.lower() == ".md":
                require(unquote(url.fragment) in anchors(read_source(root, relative)), f"broken local link fragment in {path}")


def validate_workflow(root: Path) -> None:
    workflow = record(parse_json(read_source(root, Path(".github/workflows/ci.yml")), "workflow"), "workflow")
    require(workflow.get("on") == {"pull_request": {"types": ["opened", "reopened", "synchronize", "edited"]}},
            "workflow must run on unfiltered pull_request events only")
    require(workflow.get("permissions") == {"contents": "read"}, "workflow permissions must be contents:read")
    require(workflow.get("concurrency") == {"group": "lina-os-ci-${{ github.event.pull_request.number }}",
                                            "cancel-in-progress": True}, "workflow PR concurrency is invalid")
    jobs = record(workflow.get("jobs"), "workflow jobs")
    require(set(jobs) == {"contracts", "security", "dev-gate", "release-gate"}, "workflow job set is invalid")
    for name, value in jobs.items():
        job = record(value, name)
        require(job.get("runs-on") == "ubuntu-24.04", "workflow runner must be ubuntu-24.04")
        timeout = job.get("timeout-minutes")
        require(type(timeout) is int and 1 <= timeout <= 10, "workflow timeout must be bounded")
        require("permissions" not in job and "continue-on-error" not in job, "job cannot override permissions or failures")
        steps = job.get("steps")
        require(isinstance(steps, list) and bool(steps), "workflow steps must be an array")
        for step in steps:
            record(step, "workflow step")
            require("continue-on-error" not in step and "if" not in step, "step cannot skip or suppress failures")
        checkout = record(steps[0], "checkout step")
        require(checkout.get("uses") == CHECKOUT, "workflow checkout must use the reviewed SHA")
        require(checkout.get("with") == {"persist-credentials": False, "fetch-depth": 0 if name == "security" else 1},
                "workflow checkout must use the merge candidate without credentials")
        if name in {"contracts", "security"}:
            require("needs" not in job and "if" not in job, "source jobs must run independently")
            require([step.get("run") for step in steps[1:]] == SOURCE_COMMANDS[name], "required source commands are missing or changed")
        else:
            operator = "==" if name == "release-gate" else "!="
            require(job.get("if") == f"always() && github.base_ref {operator} 'main'", "gate must always aggregate its target")
            require(job.get("needs") == ["contracts", "security"], "gate prerequisites are invalid")
            require(len(steps) == 2 and steps[1].get("run") == "python3 scripts/ci/gate.py", "gate must only aggregate results")


def validate_forms(root: Path, files: list[Path]) -> None:
    for path in files:
        if str(path).startswith(".github/ISSUE_TEMPLATE/") and path.suffix in {".yml", ".yaml"}:
            form = record(parse_json(read_source(root, path), str(path)), str(path))
            if path.stem == "config":
                require(type(form.get("blank_issues_enabled")) is bool, "issue config must specify blank_issues_enabled")
            else:
                for field in ("name", "description"):
                    nonempty(form.get(field), f"issue form {field}")
                require(isinstance(form.get("body"), list) and bool(form["body"]), "issue form body must be an array")


def main() -> None:
    arguments = parser(__doc__)
    arguments.add_argument("--source-only", action="store_true", help="check manifest/docs before CI files are available")
    args = arguments.parse_args()
    root = args.root.resolve()
    files = source_files(root)
    validate_modules(root)
    for path in REQUIRED_DOCS:
        read_source(root, Path(path))
    validate_links(root, files)
    if not args.source_only:
        validate_workflow(root)
        validate_forms(root, files)
    print("contracts: passed")


if __name__ == "__main__":
    run(main)
