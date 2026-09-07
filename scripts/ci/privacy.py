"""Reject private source artifacts, personal identifiers and commit emails."""

import ipaddress
from pathlib import Path
import re

from repository import MAX_SOURCE_BYTES, git, history_commits, parser, read_source, require, run, source_files

HOME = re.compile(r"(?:/(?:home|Users)/[A-Za-z0-9_.-]+|[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9_.-]+)")
TAILNET = re.compile(r"\b(?:[a-z0-9-]+\.)*tail[a-z0-9]+\.ts\.net\b", re.I)
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
NOREPLY = re.compile(r"(?:[A-Za-z0-9+_.\[\]-]+@users\.noreply\.github\.com|noreply@github\.com)\Z")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
PRIVATE_NETWORKS = tuple(ipaddress.ip_network((address, prefix)) for address, prefix in
                         ((0x0A000000, 8), (0xAC100000, 12), (0xC0A80000, 16),
                          (0x64400000, 10), (0xA9FE0000, 16)))
PRIVATE_DIRS = {".lina", ".codex", ".codexclaw", ".ouroboros", ".re0", ".ssh", ".aws",
                "devlog", "runtime", "secrets", "node_modules", "__pycache__", "browser-profile"}
PRIVATE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".qcow2", ".img", ".iso", ".vmdk", ".vdi",
                    ".sqlite", ".sqlite3", ".db", ".log", ".pyc"}


def check_path(path: Path) -> None:
    forbidden = bool(set(path.parts) & PRIVATE_DIRS) or path.suffix.lower() in PRIVATE_SUFFIXES
    forbidden |= path.name.startswith(".env") and path.name != ".env.example"
    forbidden |= path.name in {"PLANNING_TRANSFER.json", "id_rsa", "id_ed25519", "seed.iso", "credentials.json"}
    require(not forbidden, f"forbidden source file: {path}")


def check_text(text: str, label: str) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        private = bool(HOME.search(line) or TAILNET.search(line))
        private |= any(not NOREPLY.fullmatch(value) for value in EMAIL.findall(line))
        for value in IPV4.findall(line):
            try:
                address = ipaddress.ip_address(value)
            except ValueError:
                continue
            private |= any(address in network for network in PRIVATE_NETWORKS)
        require(not private, f"privacy finding: {label}:{number} (value redacted)")


def check_history(root: Path) -> None:
    seen = set()
    for commit in history_commits(root):
        metadata = git(root, "show", "-s", "--format=%ae%n%ce", commit).decode().splitlines()
        require(len(metadata) == 2 and all(NOREPLY.fullmatch(email) for email in metadata),
                f"non-noreply author or committer in {commit[:12]} (value redacted)")
        check_text(git(root, "show", "-s", "--format=%B", commit).decode(), f"commit {commit[:12]}")
        for entry in git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
            if not entry:
                continue
            header, name = entry.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            path = Path(name.decode())
            check_path(path)
            require(mode in {"100644", "100755"} and kind == "blob", "history contains a symlink or submodule")
            if (oid, path) in seen:
                continue
            seen.add((oid, path))
            require(int(git(root, "cat-file", "-s", oid)) <= MAX_SOURCE_BYTES, "history source file too large")
            check_text(git(root, "cat-file", "blob", oid).decode("utf-8"), str(path))


def main() -> None:
    arguments = parser(__doc__)
    arguments.add_argument("--history", action="store_true", help="also scan every reachable tree and commit metadata")
    args = arguments.parse_args()
    root = args.root.resolve()
    for path in source_files(root):
        check_path(path)
        check_text(read_source(root, path), str(path))
    if args.history:
        check_history(root)
    print(f"privacy: passed ({'worktree and history' if args.history else 'worktree only'})")


if __name__ == "__main__":
    run(main)
