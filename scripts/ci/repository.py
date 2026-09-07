"""Bounded source reads and diagnostics shared by the repository checks."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from identifiers import has_private_identifier

MAX_SOURCE_BYTES = 2 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def parse_json(text: str, label: str) -> object:
    try:
        return json.loads(text, object_pairs_hook=unique_object)
    except (ValueError, RecursionError):
        raise ValueError(f"{label}: invalid JSON; must be valid JSON without duplicate keys") from None


def record(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=30)
    require(result.returncode == 0, f"Git source read failed ({args[0]})")
    return result.stdout


def source_files(root: Path) -> list[Path]:
    names = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    paths = sorted({Path(name.decode("utf-8")) for name in names.split(b"\0") if name})
    for path in paths:
        require(not has_private_identifier(str(path)), "private source filename (value redacted)")
        target = root / path
        require(not target.is_symlink(), f"source symlink is forbidden: {path}")
        require(target.resolve().is_relative_to(root), "source path escapes repository")
    return paths


def read_source(root: Path, path: Path) -> str:
    target = root / path
    require(target.is_file(), f"required file missing: {path}")
    require(target.stat().st_size <= MAX_SOURCE_BYTES, f"source file too large: {path}")
    try:
        return target.read_text(encoding="utf-8")
    except UnicodeError:
        raise ValueError(f"source must be UTF-8 text: {path}") from None


def history_commits(root: Path) -> list[str]:
    require(git(root, "rev-parse", "--is-shallow-repository").strip() == b"false",
            "history requires a complete, non-shallow checkout")
    commits = git(root, "rev-list", "--all").decode().splitlines()
    require(bool(commits), "history requires a commit; this repository is unborn")
    return list(dict.fromkeys(commits + git(root, "rev-list", "HEAD").decode().splitlines()))


def parser(description: str) -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=description)
    result.add_argument("--root", type=Path, default=Path.cwd(), help="repository to inspect (default: cwd)")
    return result


def run(main) -> None:
    try:
        main()
    except (ValueError, OSError, subprocess.TimeoutExpired, RecursionError) as error:
        detail = str(error) if isinstance(error, ValueError) else type(error).__name__
        print(f"ci: {detail}", file=sys.stderr)
        sys.exit(1)
