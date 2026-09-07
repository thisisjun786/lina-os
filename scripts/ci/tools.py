"""Run checksum-pinned Linux tools in temporary directories, without installs."""

import hashlib
import io
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import tempfile
import tomllib
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from repository import MAX_SOURCE_BYTES, git, history_commits, parse_json, parser, read_source, require, run, source_files

TOOLS = {
    "actionlint": ("rhysd/actionlint", "1.7.12", "actionlint_1.7.12_linux_amd64.tar.gz",
                   "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"),
    "gitleaks": ("gitleaks/gitleaks", "8.30.1", "gitleaks_8.30.1_linux_x64.tar.gz",
                 "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"),
}
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_HISTORY_BYTES = 64 * 1024 * 1024


class ReleaseRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        require(parsed.scheme == "https" and parsed.hostname in {"github.com", "release-assets.githubusercontent.com"}
                and not parsed.username and not parsed.password and parsed.port in {None, 443},
                "tool download redirected outside public GitHub releases")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def unpack_verified(data: bytes, expected: str, name: str, destination: Path) -> Path:
    require(hashlib.sha256(data).hexdigest() == expected, "tool archive checksum mismatch")
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            member = archive.getmember(name)
            require(member.isfile() and member.size <= MAX_ARCHIVE_BYTES, "tool must be a bounded regular file")
            content = archive.extractfile(member).read()
    except (tarfile.TarError, KeyError):
        raise ValueError("tool archive is invalid") from None
    binary = destination / name
    binary.write_bytes(content)
    binary.chmod(0o700)
    return binary


def download(name: str, destination: Path) -> Path:
    require(platform.system() == "Linux" and platform.machine() in {"x86_64", "amd64"},
            "pinned tools require Linux amd64; Python contracts are platform independent")
    repository, version, archive, checksum = TOOLS[name]
    url = f"https://github.com/{repository}/releases/download/v{version}/{archive}"
    opener = build_opener(ProxyHandler({}), ReleaseRedirects())
    try:
        with opener.open(Request(url, headers={"User-Agent": "lina-os-source-ci"}), timeout=30) as response:
            content = response.read(MAX_ARCHIVE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ValueError("tool download failed; no unverified binary was executed") from None
    require(len(content) <= MAX_ARCHIVE_BYTES, "tool archive is too large")
    return unpack_verified(content, checksum, name, destination)


def history_input(root: Path) -> bytes:
    """Read all reachable content without inheriting scanner path exclusions."""
    content, seen_blobs, seen_names = bytearray(), set(), set()

    def append(value: bytes) -> None:
        require(len(content) + len(value) + 1 <= MAX_HISTORY_BYTES,
                "history scan exceeds its explicit input limit; no content was skipped")
        content.extend(value)
        content.extend(b"\n")

    for commit in history_commits(root):
        append(git(root, "show", "-s", "--format=%B", commit))
        for entry in git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
            if not entry:
                continue
            header, name = entry.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            require(kind == "blob" and mode in {"100644", "100755"},
                    "history contains a non-text source entry")
            if name not in seen_names:
                append(name)
                seen_names.add(name)
            if oid not in seen_blobs:
                require(int(git(root, "cat-file", "-s", oid)) <= MAX_SOURCE_BYTES,
                        "historical source exceeds its file limit")
                append(git(root, "cat-file", "blob", oid))
                seen_blobs.add(oid)
    return bytes(content)


def scan(binary: Path, root: Path, config: Path, work: Path, mode: str = "git") -> int:
    ignore = work / "empty.ignore"
    ignore.write_text("")
    report = work / "findings.json"
    report.write_text("null")
    command = [str(binary), "stdin" if mode == "history-stdin" else mode]
    if mode == "git":
        command += [git(root, "rev-parse", "--absolute-git-dir").decode().strip(), "--log-opts=--all -m HEAD"]
    command += ["--config", str(config), "--gitleaks-ignore-path", str(ignore),
                "--ignore-gitleaks-allow", "--redact=100", "--no-banner",
                "--report-format=json", "--report-path", str(report)]
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GITLEAKS_")}
    content = None
    if mode == "stdin":
        content = "\n".join(str(path) + "\n" + read_source(root, path) for path in source_files(root)).encode()
    elif mode == "history-stdin":
        content = history_input(root)
    result = subprocess.run(command, cwd=work, env=environment, input=content, capture_output=True, timeout=120)
    # Never echo scanner output, which may contain commit identities or file content.
    require(result.returncode in {0, 1}, "Gitleaks execution failed")
    findings = parse_json(report.read_text(), "Gitleaks report")
    require(isinstance(findings, list) and bool(findings) == (result.returncode == 1),
            "Gitleaks failed without a matching findings report")
    if mode == "git" and result.returncode == 0:
        return scan(binary, root, config, work, "history-stdin")
    return result.returncode


def main() -> None:
    arguments = parser(__doc__)
    arguments.add_argument("tool", choices=("actionlint", "secrets"))
    arguments.add_argument("--self-test-only", action="store_true", help="secrets: test synthetic histories only")
    args = arguments.parse_args()
    root = args.root.resolve()
    require(not args.self_test_only or args.tool == "secrets", "self-test-only requires secrets")
    if args.tool == "secrets" and not args.self_test_only:
        history_commits(root)
    with tempfile.TemporaryDirectory(prefix="lina-os-ci-") as directory:
        work = Path(directory)
        binary = download("gitleaks" if args.tool == "secrets" else "actionlint", work)
        if args.tool == "actionlint":
            result = subprocess.run([str(binary), "-shellcheck=", "-pyflakes=", ".github/workflows/ci.yml"],
                                    cwd=root, timeout=30)
            require(result.returncode == 0, "actionlint rejected the workflow")
        else:
            source_config = tomllib.loads(read_source(root, Path(".gitleaks.toml")))
            require(set(source_config) <= {"title", "extend"} and source_config.get("extend") == {"useDefault": True},
                    "Gitleaks configuration must use default rules without overrides")
            config = work / "gitleaks.toml"
            config.write_text(read_source(root, Path(".gitleaks.toml")))
            from secret_fixtures import verify_scanner
            verify_scanner(binary, config, work)
            if not args.self_test_only:
                require(scan(binary, root, config, work) == 0, "Gitleaks history secret detected (value redacted)")
                require(scan(binary, root, config, work, "stdin") == 0, "Gitleaks worktree secret detected (value redacted)")
        print(f"{args.tool}: passed" + (" (synthetic histories only)" if args.self_test_only else ""))


if __name__ == "__main__":
    run(main)
