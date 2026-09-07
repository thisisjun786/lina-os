"""Probe pinned Lina sources without credentials or arbitrary network targets."""

from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from contracts import PUBLIC_REPOSITORY, links, validate_modules
from repository import MAX_SOURCE_BYTES, parse_json, parser, read_source, record, require, run, source_files


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("upstream redirect refused")


def public_get(url: str) -> bytes:
    # No netrc, auth handler, cookies, proxy credentials or ambient GitHub token.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    request = Request(url, headers={"User-Agent": "lina-os-source-ci", "Accept": "application/vnd.github+json"})
    try:
        with opener.open(request, timeout=15) as response:
            require(response.status == 200, "upstream response must be HTTP 200")
            content = response.read(MAX_SOURCE_BYTES + 1)
    except HTTPError as error:
        raise ValueError(f"upstream HTTP {error.code}; public reference unavailable") from None
    except (URLError, TimeoutError, OSError):
        raise ValueError("upstream network error; public reference unverified") from None
    require(0 < len(content) <= MAX_SOURCE_BYTES, "upstream response is empty or too large")
    return content


def public_targets(root, revision: str) -> list[str]:
    targets = set()
    for path in source_files(root):
        if path.suffix.lower() != ".md":
            continue
        for link in links(read_source(root, path)):
            parsed = urlsplit(link)
            if parsed.hostname != "github.com" or not parsed.path.lower().startswith("/thisisjun786/lina/blob/"):
                continue
            prefix = f"{PUBLIC_REPOSITORY}/blob/{revision}/"
            require(link.startswith(prefix) and not parsed.query, f"invalid public source link in {path}")
            target = unquote(parsed.path[len(f"/thisisjun786/lina/blob/{revision}/"):])
            require(bool(target) and all(part not in {"", ".", ".."} for part in target.split("/"))
                    and not any(char in target for char in "\\\r\n\0"), f"invalid public source link path in {path}")
            require(not PurePosixPath(target).is_absolute(), f"invalid public source link in {path}")
            targets.add(target)
    require(bool(targets), "at least one pinned public source link is required")
    return sorted(targets)


def main() -> None:
    root = parser(__doc__).parse_args().root.resolve()
    manifest = validate_modules(root)
    revision = manifest["productSourceRevision"]
    targets = public_targets(root, revision)
    response = public_get(f"https://api.github.com/repos/thisisjun786/lina/commits/{revision}")
    commit = record(parse_json(response.decode("utf-8"), "upstream commit"), "upstream commit")
    require(commit.get("sha") == revision, "upstream revision mismatch")
    for target in targets:
        public_get(f"https://raw.githubusercontent.com/thisisjun786/lina/{revision}/{quote(target, safe='/')}")
    print(f"public references: passed ({len(targets)} files; {revision})")


if __name__ == "__main__":
    run(main)
