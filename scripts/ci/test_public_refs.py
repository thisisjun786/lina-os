import subprocess
import sys

from test_support import PIN, PUBLIC, RepositoryCase, SCRIPTS


class PublicReferencesTests(RepositoryCase):
    def probe(self, response="success"):
        # Mock only the network boundary; execute the real CLI and all URL validation.
        program = '''
import io, json, pathlib, runpy, sys, urllib.error
from unittest.mock import patch
mode, script, pin = sys.argv[1:]
sys.path.insert(0, str(pathlib.Path(script).parent))
sys.argv = [script]
def opened(opener, request, **kwargs):
    if mode.isdigit():
        raise urllib.error.HTTPError(request.full_url, int(mode), "fixture", {}, None)
    if mode == "network":
        raise urllib.error.URLError("synthetic outage")
    if "api.github.com" in request.full_url:
        payload = json.dumps({"sha": pin if mode != "mismatch" else "0" * 40}).encode()
    else:
        payload = b"# Public fixture\\n"
    result = io.BytesIO(payload)
    result.status = 200
    return result
with patch("urllib.request.OpenerDirector.open", opened):
    runpy.run_path(script, run_name="__main__")
'''
        return subprocess.run([sys.executable, "-c", program, response,
                               str(SCRIPTS / "public_refs.py"), PIN], cwd=self.root,
                              env=self.env, capture_output=True, text=True, timeout=20)

    def test_public_commit_and_target_success(self):
        self.passes(self.probe(), "public references: passed")

    def test_upstream_http_network_and_payload_failures(self):
        for mode, message in (("404", "upstream HTTP 404"), ("422", "upstream HTTP 422"),
                              ("network", "upstream network error"),
                              ("mismatch", "upstream revision mismatch")):
            with self.subTest(mode=mode):
                self.fails(self.probe(mode), message)

    def test_unpinned_or_escaping_product_links(self):
        for path in ("blob/main/README.md", f"blob/{PIN}/../secret", f"blob/{PIN}/README.md?token=value"):
            self.write("README.md", f"[Bad]({PUBLIC}/{path})\n")
            self.fails(self.probe(), "public source link")

    def test_upstream_pr_and_issue_links_are_not_source_pins(self):
        self.write("README.md", f"[Source]({PUBLIC}/blob/{PIN}/README.md)\n"
                   f"[PR]({PUBLIC}/pull/1)\n[Issue]({PUBLIC}/issues/1)\n")
        self.passes(self.probe(), "public references: passed")

    def test_repository_url_cannot_redirect_probes(self):
        self.modules["productRepository"] = "http://localhost/private"
        self.save_modules()
        self.fails(self.probe(), "public Lina repository")
