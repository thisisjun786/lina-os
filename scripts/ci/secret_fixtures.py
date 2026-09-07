"""Real Gitleaks regressions on disposable histories; no candidate ref writes."""

import os
from pathlib import Path
import random
import string
import subprocess

from repository import require


def verify_scanner(binary: Path, config: Path, work: Path) -> None:
    from tools import scan

    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                        "GIT_AUTHOR_NAME": "Fixture", "GIT_COMMITTER_NAME": "Fixture",
                        "GIT_AUTHOR_EMAIL": "123+fixture@users.noreply.github.com",
                        "GIT_COMMITTER_EMAIL": "noreply@github.com"})
    token = "ghp_" + "".join(random.Random(946).sample(string.ascii_letters + string.digits, 36))
    for scenario in ("removed", "merge", "removed-svg", "removed-lockfile"):
        root = work / scenario
        root.mkdir()

        def git(*args):
            result = subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", *args],
                                    env=environment, capture_output=True, text=True, timeout=15)
            require(result.returncode == 0, "synthetic Git setup failed")
            return result.stdout.strip()

        def commit():
            git("add", ".")
            git("commit", "-qm", "Synthetic fixture")

        git("init", "-q", "-b", "dev")
        (root / "README.md").write_text("Synthetic source\n")
        commit()
        require(scan(binary, root, config, work) == 0, "Gitleaks clean history self-test failed")
        if scenario == "merge":
            git("checkout", "-qb", "side")
            (root / "side.md").write_text("Side\n")
            commit()
            git("checkout", "-q", "dev")
            (root / "dev.md").write_text("Dev\n")
            commit()
            git("merge", "--no-ff", "--no-commit", "side")
        leak_path = {"removed-svg": "image.svg", "removed-lockfile": "package-lock.json"}.get(scenario, "leak.py")
        (root / leak_path).write_text('token = "' + token + '" # gitleaks:allow\n')
        commit()
        sha = git("rev-parse", "HEAD")
        if scenario == "merge":
            require(len(git("show", "-s", "--format=%P", "HEAD").split()) == 2,
                    "synthetic secret must exist only in a merge commit")
        (root / leak_path).unlink()
        (root / ".gitleaksignore").write_text(f"{sha}:{leak_path}:github-pat:1\n")
        commit()
        old = os.environ.get("GITLEAKS_CONFIG_TOML")
        os.environ["GITLEAKS_CONFIG_TOML"] = '[allowlist]\npaths = [".*"]\n'
        try:
            require(scan(binary, root, config, work) == 1,
                    f"Gitleaks {scenario} history self-test missed a synthetic secret")
        finally:
            if old is None:
                os.environ.pop("GITLEAKS_CONFIG_TOML", None)
            else:
                os.environ["GITLEAKS_CONFIG_TOML"] = old
    print("Gitleaks self-tests: clean, removed, merge, removed SVG/lockfile, ignore overrides passed")
