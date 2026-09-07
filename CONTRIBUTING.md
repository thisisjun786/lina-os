# Contributing to Lina OS

Lina OS currently contains composition specifications and implementation plans.
Start with [README](README.md), [planning](docs/PLANNING.md) and
[POLICY](POLICY.md). Product runtime changes belong in
[Lina](https://github.com/thisisjun786/lina).

1. Branch from current `dev`, preferably in an isolated checkout/worktree.
2. Make one coherent change and run the relevant [source checks](docs/CI.md).
3. Open a PR to `dev`. Explain the problem, resulting behavior, actual checks and
   material limitations. An issue is optional for a small fix.
4. Resolve material findings and discussions. The owner merges after the current
   candidate passes `dev-gate` and is current with the base.

The bug, feature, compatibility and design-decision forms are prompts, not
mandatory paperwork. For compatibility reports include relevant OS/kernel/GPU,
Lina source revision, desktop backend and external tool versions. Distinguish
installed, configured and actually exercised capabilities.

Use synthetic data and a no-reply commit email. Do not upload private logs,
tokens, browser state, disk images or personal installation inventories.
Report vulnerabilities using [SECURITY](SECURITY.md).

`main` source promotion requires explicit owner instruction and release notes.
OS installation, artifact publication and deployment require their own evidence
and authorization. A green source check does not complete those steps.

Original contributions are accepted under [Apache-2.0](LICENSE). Identify any
third-party material and preserve its applicable license and attribution.
