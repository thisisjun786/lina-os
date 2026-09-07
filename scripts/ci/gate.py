"""Aggregate exact prerequisites without rerunning source checks."""

import os
import re

from repository import parse_json, record, require, run


def main() -> None:
    names = ("NEEDS_JSON", "EXPECTED_RELEASE", "BASE_REF", "HEAD_REF", "BASE_REPO",
             "HEAD_REPO", "BASE_REPO_ID", "HEAD_REPO_ID")
    for name in names:
        require(bool(os.environ.get(name)), f"{name} is required")
    release = os.environ["EXPECTED_RELEASE"]
    require(release in {"true", "false"}, "EXPECTED_RELEASE must be true or false")
    require((release == "true") == (os.environ["BASE_REF"] == "main"),
            "release mode does not match the target branch")
    for name in ("BASE_REPO_ID", "HEAD_REPO_ID"):
        require(bool(re.fullmatch(r"[1-9][0-9]*", os.environ[name])), f"{name} must be a repository ID")
    if release == "true":
        require(os.environ["HEAD_REF"] == "dev"
                and os.environ["BASE_REPO"] == os.environ["HEAD_REPO"]
                and os.environ["BASE_REPO_ID"] == os.environ["HEAD_REPO_ID"],
                "main requires a same-repository dev head")
    needs = record(parse_json(os.environ["NEEDS_JSON"], "needs"), "needs")
    require(set(needs) == {"contracts", "security"}, "needs must contain exactly contracts and security")
    for name in ("contracts", "security"):
        job = record(needs[name], name)
        require(job.get("result") == "success", f"{name} must succeed")
        require(set(job) <= {"result", "outputs"}, f"{name} has unexpected result fields")
        if "outputs" in job:
            record(job["outputs"], f"{name}.outputs")
    print(f"{'release' if release == 'true' else 'dev'}-gate: passed")


if __name__ == "__main__":
    run(main)
