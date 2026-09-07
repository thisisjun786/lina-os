# Lina OS repository policy

This repository owns its development, CI and source-release policy. Lina is the
product runtime owner and a compatibility dependency, not a shared CI authority.
Prefer small changes, fast feedback and clear evidence for a solo maintainer.

## Branches and authority

| Target | Purpose | Required check | Merge method |
| --- | --- | --- | --- |
| `dev` | Default branch; normal integration | `dev-gate` | Merge commit |
| `main` | Explicit source promotion from this repository's `dev` | `release-gate` | Merge commit |

Use short-lived branches such as `codex/module-validation`. All normal PRs target
`dev`; intermediate development PRs receive the same source checks. Before merge,
confirm current head/base, green required checks, base freshness, no conflicts,
resolved review conversations and no known material defect. Use an expected-head
guard. Do not directly push protected branches, force-push or bypass protection.

Required human approvals are zero. Automated reviews are advisory; confirmed
defects still need resolution. Agents may complete integration within the user's
authorized delivery scope. Every `dev` to `main` promotion needs explicit owner
instruction and release notes for that promotion. Do not infer image publishing,
package publishing, deployment, provider calls or installed-data changes from it.

GitHub must separately enforce PRs, strict required checks, resolved conversations,
admin enforcement, and disabled force pushes/deletions on both branches. The
workflow alone does not activate those settings. Recheck them after visibility
changes; repository owners can still change rules and workflow source.

## Source checks

Run `contracts` and `security` independently, followed by result-only gates.
Every PR runs both checks; this small repository needs no docs-only selector.
The gate rejects failure, cancellation, missing/malformed results and unexpected
skips. `main` accepts only a same-repository `dev` head. Test GitHub's combined
merge candidate, not just the contributor branch. Do not rerun tests in gates.

Use standard hosted Ubuntu runners, read-only tokens, pinned Action revisions,
checksum-verified tools, bounded timeouts and cancellation of obsolete runs of
the same PR. Do not duplicate the suite on push. PR code uses `pull_request`,
without production secrets, self-hosted runners or privileged execution through
`pull_request_target`. CI does not install the product or call model providers.

Use the smallest meaningful local checks while developing. [CI](docs/CI.md)
defines executable commands and coverage. Changes to CI must exercise failed,
cancelled, skipped and malformed prerequisite results, plus branch/repository
source restrictions. Workflow edits still require maintainer review: tests of
the workflow are not an absolute barrier against malicious workflow changes.

## Dependencies and acceptance

[modules.json](modules.json) owns the selected Lina source revision. Keep it
publicly retrievable and immutable; record the upstream change and affected
consumer contracts when updating it. Keep product-document links at that same
revision. An upstream build or source lookup proves neither OS compatibility nor
successful installation. Do not update running services as part of a pin change.

Lina owns native product tests. Lina OS owns its composition and installation
tests; avoid copying the whole product suite here. Add installer, image and guest
checks when their implementation exists. OS releases require the artifact,
component versions, integrity/license notices and actual guest/host evidence in
[ACCEPTANCE](docs/ACCEPTANCE.md), including negative and recovery scenarios.
The source release gate alone cannot certify boot, shared login or GUI control.

## Public source and preservation

Publish authored product requirements and source, not operational records, user
data or private Git history. Scan all available history including merge diffs;
ignore inline secret-allow comments and repository ignore files. Privacy checks
supplement secret scanning; neither proves the absence of every unknown secret.
Review exact synthetic exceptions, never blanket-baseline findings away.

Use no-reply commit identities for project work and keep valid third-party
attribution. Before source publication inspect final remote refs and metadata,
PRs, issues, Actions output and attachments as described in
[PUBLICATION](docs/PUBLICATION.md). Preserve private archives separately.

Use short issue/PR templates without mandatory issue creation or keyword bots.
Respect review-only and local-only scopes. Never reset, clean, stash, rebase or
delete someone else's work. Report local verification, hosted CI, merge,
source visibility and OS deployment as distinct outcomes.
