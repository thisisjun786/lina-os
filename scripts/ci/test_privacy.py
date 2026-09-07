from test_support import RepositoryCase


class PrivacyTests(RepositoryCase):
    def test_private_filenames_are_rejected_without_echoing_them(self):
        names = ["192." + "168.55.9.md", "person" + "@private.invalid.md"]
        for name in names:
            with self.subTest(kind=name.rsplit(".", 1)[-1]):
                self.write(name, "Safe contents\n")
                result = self.cli("privacy")
                self.fails(result, "private source filename")
                self.assertNotIn(name, result.stdout + result.stderr)
                (self.root / name).unlink()

    def test_removed_private_filename_is_rejected_and_redacted(self):
        name = "notes/person" + "@private.invalid.md"
        self.write(name, "Safe contents\n")
        self.commit()
        (self.root / name).unlink()
        self.commit()
        result = self.cli("privacy", "--history")
        self.fails(result, "private source filename")
        self.assertNotIn(name, result.stdout + result.stderr)

    def test_clean_worktree(self):
        self.passes(self.cli("privacy"), "privacy: passed")

    def test_personal_home_network_and_email_values_are_redacted(self):
        values = ["/" + "home/fixture-owner/private", "/" + "Users/fixture-owner/private",
                  "192." + "168.55.9", "100." + "80.55.9", "tail" + "abc123.ts.net",
                  "person" + "@private.invalid"]
        for value in values:
            with self.subTest(value=value):
                self.write("README.md", value)
                result = self.cli("privacy")
                self.fails(result, "privacy finding")
                self.assertNotIn(value, result.stdout + result.stderr)

    def test_scripts_are_not_excluded(self):
        self.write("scripts/ci/unexpected.py", "# /" + "home/fixture-owner/private")
        self.fails(self.cli("privacy"), "privacy finding")

    def test_notice_files_have_no_blanket_email_exception(self):
        for path in ("LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"):
            with self.subTest(path=path):
                self.write(path, "person" + "@private.invalid")
                self.fails(self.cli("privacy"), "privacy finding")
                self.write(path, "Public attribution\n")

    def test_tracked_ignored_runtime_file(self):
        self.write(".gitignore", ".env\n")
        self.write(".env", "EXAMPLE=value\n")
        self.git("add", "-f", ".env")
        self.fails(self.cli("privacy"), "forbidden source file")

    def test_unborn_history_fails_explicitly(self):
        self.fails(self.cli("privacy", "--history"), "history requires a commit")

    def test_github_noreply_metadata(self):
        self.commit()
        self.passes(self.cli("privacy", "--history"), "privacy: passed")

    def test_non_noreply_metadata_and_removed_private_content(self):
        self.env["GIT_AUTHOR_EMAIL"] = "person" + "@private.invalid"
        self.commit()
        self.fails(self.cli("privacy", "--history"), "non-noreply author or committer")

    def test_removed_private_content_in_history(self):
        self.write("private.md", "/" + "home/fixture-owner/private")
        self.commit()
        (self.root / "private.md").unlink()
        self.commit()
        self.fails(self.cli("privacy", "--history"), "privacy finding")
