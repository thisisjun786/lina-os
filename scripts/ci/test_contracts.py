import json

from test_support import RepositoryCase


class ContractsTests(RepositoryCase):
    def test_valid_modules_and_links(self):
        self.passes(self.cli("contracts", "--source-only"), "contracts: passed")

    def test_undefined_profile_module(self):
        self.modules["profiles"]["os"].append("undefined")
        self.save_modules()
        self.fails(self.cli("contracts", "--source-only"), "undefined profile module")

    def test_schema_types_keys_and_pin(self):
        for key, value, message in (
            ("schemaVersion", True, "schemaVersion must be 1"),
            ("status", "implemented", "status must be design"),
            ("extra", "value", "modules.json keys"),
            ("productSourceRevision", "", "40-character source revision"),
            ("productSourceRevision", "main", "40-character source revision"),
            ("profiles", [], "profiles must be an object"),
            ("modules", {"bad": {"owner": "lina", "status": 0}}, "module status"),
            ("productRepository", "https://example.com/private", "public Lina repository"),
        ):
            with self.subTest(key=key, value=value):
                saved = dict(self.modules)
                self.modules[key] = value
                self.save_modules()
                self.fails(self.cli("contracts", "--source-only"), message)
                self.modules = saved

    def test_malformed_and_duplicate_json(self):
        for content in ("{", '{"schemaVersion": 1, "schemaVersion": 2}'):
            self.write("modules.json", content)
            self.fails(self.cli("contracts", "--source-only"), "invalid JSON")

    def test_broken_local_links_and_fragments(self):
        for target in ("missing.md", "docs/CI.md#absent", "../outside.md"):
            self.write("README.md", f"[Broken]({target})\n")
            self.fails(self.cli("contracts", "--source-only"), "local link")

    def test_reference_links_and_symlinks(self):
        self.write("README.md", "[broken][ref]\n\n[ref]: missing.md\n")
        self.fails(self.cli("contracts", "--source-only"), "local link")
        self.write("README.md", "[read](escape.md)\n")
        (self.root / "escape.md").symlink_to(self.root.parent / "outside.md")
        self.fails(self.cli("contracts", "--source-only"), "symlink")

    def test_module_optional_fields_are_typed(self):
        self.modules["modules"]["omo-native"]["independentLifecycle"] = "true"
        self.save_modules()
        self.fails(self.cli("contracts", "--source-only"), "independentLifecycle must be true")

    def test_missing_public_document_is_not_skipped(self):
        (self.root / "POLICY.md").unlink()
        self.fails(self.cli("contracts", "--source-only"), "required file missing: POLICY.md")
