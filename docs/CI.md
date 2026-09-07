# Source CI

[POLICY](../POLICY.md) owns integration and release decisions. This repository
currently contains design/composition source, so its checks do not build an OS
or install Lina. No model-provider credentials or local services are required.

## Local checks

Run from a Git checkout with Python 3.12 or newer:

```sh
python3 -m unittest discover -s scripts/ci -p 'test_*.py'
python3 scripts/ci/contracts.py
python3 scripts/ci/public_refs.py
python3 scripts/ci/privacy.py --history
python3 scripts/ci/tools.py actionlint
python3 scripts/ci/tools.py secrets
git diff --check
```

Contracts, public-reference and privacy commands accept `--root PATH` to inspect
a different checkout. The privacy/history check requires a committed, complete
Git history; an unborn or shallow repository is an error. Tests use isolated,
synthetic repositories and controlled network responses. The public-reference
command makes real unauthenticated requests and fails on unavailable sources.

The tool launcher downloads pinned Linux x86-64 releases to temporary directories
and verifies their checksums. It installs nothing globally. The secret command
also exercises synthetic secret histories and scans both source and history.
See [the executable workflow](../.github/workflows/ci.yml) and
[CI scripts](../scripts/ci) for the commands and checksum pins. For source-only
privacy feedback before the first commit, omit `--history`; this does not verify
commit metadata or deleted files.

## Job graph

| Job | Checks |
| --- | --- |
| `contracts` | CI-control tests, workflow/forms, module schema and profile references, local links, public Lina source and matching documentation references |
| `security` | Source/history privacy and no-reply metadata; Gitleaks across full Git history including merge diffs |
| `dev-gate` | Requires successful contracts/security for development PRs |
| `release-gate` | Same source checks; additionally requires this repository's `dev` as the head of a `main` PR |

Both prerequisite jobs run in parallel on every PR. Gates run even when a
prerequisite fails and aggregate results without repeating the checks. Missing,
failed, cancelled, skipped or malformed prerequisites cannot pass. A fork branch
called `dev` is not accepted for `main` promotion.

Checkout uses GitHub's merge candidate and does not retain credentials. Only
`pull_request` triggers the suite, with no path filters or duplicate push run.
Older executions of the same PR are cancelled. Standard hosted Ubuntu runners,
read-only tokens, pinned/checksummed tools and bounded timeouts keep the source
checks independent of maintainer machines and runtime services.

## Activation and changes

Set the default branch to `dev` and allow merge commits only. Protect both `dev`
and `main` with PRs, strict required checks (`dev-gate` and `release-gate`
respectively), resolved conversations and admin enforcement. Disable force pushes
and deletions; required human review count is zero. Pin each required check to
the GitHub Actions app after observing an actual run. Read settings back after
configuration and after any visibility change.

For CI changes, exercise success and refusal with synthetic bad input. Inspect
the actual failed prerequisite and final gate, and confirm GitHub reports the PR
blocked by its required check. Fix forward and verify the current head before
merging. Do not weaken a check merely to pass a failing run.

## Coverage limits

These checks validate repository source and declared dependencies. They do not
prove that a referenced Lina revision boots, supports a particular GPU, shares
a login, fences stale input or survives OS recovery. Installer/image/guest tests
must accompany those implementations. Release evidence must satisfy
[ACCEPTANCE](ACCEPTANCE.md) for the actual artifacts and environments claimed.

Secret and privacy checks cannot identify every unknown sensitive value. Workflow
authors can also change the checker; maintainer review and GitHub protection are
part of the control. [PUBLICATION](PUBLICATION.md) covers the final hosted logs,
metadata and attachment review that local source checks cannot replace.
