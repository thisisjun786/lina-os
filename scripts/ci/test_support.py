"""Independent, synthetic source fixtures for CLI acceptance tests."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
PIN = "e41ce13bf4566f5850936742186e1643266959e9"
PUBLIC = "https://github.com/thisisjun786/lina"


class RepositoryCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                         "GIT_AUTHOR_NAME": "Fixture", "GIT_COMMITTER_NAME": "Fixture",
                         "GIT_AUTHOR_EMAIL": "123+fixture@users.noreply.github.com",
                         "GIT_COMMITTER_EMAIL": "noreply@github.com",
                         "PYTHONDONTWRITEBYTECODE": "1"})
        self.git("init", "-q", "-b", "dev")
        self.write(".gitignore", "__pycache__/\n")
        self.modules = {
            "schemaVersion": 1, "status": "design", "productRepository": PUBLIC,
            "productSourceRevision": PIN, "dataHome": "LINA_HOME or ~/.lina",
            "profiles": {"native": ["lina-runtime"], "dedicated-computer": ["lina-runtime"],
                         "os": ["lina-runtime", "omo-native"]},
            "modules": {"lina-runtime": {"owner": "lina", "status": "source-pinned"},
                        "omo-native": {"owner": "external", "status": "development-tool",
                                       "independentLifecycle": True}},
            "isolation": {"direct": "declared host", "task-container": "planned",
                          "runtime-container": "external packaging"},
        }
        self.save_modules()
        for path in ("README.md", "AGENTS.md", "POLICY.md", "CONTRIBUTING.md", "SECURITY.md",
                     "LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "docs/CI.md",
                     "docs/PUBLICATION.md", "docs/PLANNING.md", "docs/ACCEPTANCE.md"):
            self.write(path, "# Fixture\n\n## Details\n")
        self.write("README.md", f"# Fixture\n[Local](docs/CI.md#details)\n"
                   f"[Public]({PUBLIC}/blob/{PIN}/README.md)\n")

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def save_modules(self):
        self.write("modules.json", json.dumps(self.modules))

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=True).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic fixture")

    def cli(self, name, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPTS / f"{name}.py"), *args],
                              cwd=self.root, env=self.env | (env or {}),
                              capture_output=True, text=True, timeout=20)

    def fails(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def passes(self, result, message):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)
