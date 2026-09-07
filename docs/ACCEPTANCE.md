# Delivery acceptance

These are required future runtime proofs, not completed test results.

| Capability | Required evidence |
| --- | --- |
| Reproducible composition | Exact Lina revision and artifact digest; OS and selected module pins |
| Fresh installation | Disposable VM boots with a non-developer owner name and the installed runtime |
| Mandatory onboarding | Tailscale authenticated connection, working model route, OpenCodex readiness and separately managed OmO Native installation |
| Independent desktops | Human and two agents type concurrently; input reaches only the selected desktops |
| Human takeover | Stale agent input is rejected after ownership changes; return uses a fresh screen |
| Shared login | A newly created agent uses the approved test login without repeating sign-in; conflicts are measured |
| Host capability | A declared command changes only the selected disposable host under the intended identity |
| Isolation | Forbidden host paths and sockets are unavailable; allowed mounts, egress and limits match the selected profile |
| Restart | Agent, conversation, computer and task identities survive; uncertain actions are inspected without replay |
| Recovery | Consistent local checkpoint plus required external exporters; reviewed binding/permission migration before activation |
| Update | Failed release preparation preserves the previous release; schema compatibility is checked before switching writers |
| Distribution | Component license notices, artifact integrity and current source/history privacy review before public release |

Linux product tests and its container smoke do not satisfy desktop input, physical
OS installation or native macOS/Windows acceptance. The retired project's VM code
is an optional reference only; no migration from it is required.

## Detailed planning ownership

See the [planning index](PLANNING.md) for the imported OS roadmap and the Lina-owned
computer/model/state contracts. The scenario matrices in those plans remain required
future evidence; importing the documents does not mark those checks complete.
