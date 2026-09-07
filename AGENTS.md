# Lina OS development

Read [POLICY.md](POLICY.md) before changing source, CI or repository settings.
It owns integration and release rules. Use [CONTRIBUTING.md](CONTRIBUTING.md)
and [docs/CI.md](docs/CI.md) for the contribution flow and executable checks.

Lina OS is currently a design-stage distribution project. Lina owns the product
runtime, model adapters, conversations, memory and task contracts. Do not vendor
Lina runtime sources or revive retired Senpi/OmO job packages. OmO Native remains
an independently managed development tool.

Use explicit owner, machine and task identities and `LINA_HOME` for user data.
Never embed developer homes, credentials, browser profiles, private sessions or
generated VM seeds. Keep private work notes outside tracked public source.

Start behavior changes with a failing focused test. Validate VM boot, simultaneous
GUI input, takeover fencing, restart and recovery on actual disposable guests
before claiming those capabilities. Source checks do not prove deployment.
OS installation and host changes require a concrete authorized target.

Preserve other worktrees, branches and uncommitted work. Use isolated short-lived
branches, and document actual verification and remaining limits. Routine tooling
choices stay within the authorized task; do not add repeated confirmation gates.
