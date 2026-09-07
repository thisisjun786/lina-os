# Source release notes

## Initial public source

This source release contains Lina OS composition specifications and the desktop,
host execution, onboarding, update and recovery requirements. The project remains
in the design stage; no bootable image or OS installer is included.

The manifest references an immutable public Lina revision. Product runtime source
stays in Lina, and OmO Native retains an independent development-tool lifecycle.
Original source and documentation use Apache-2.0 with third-party notices.

Repository CI checks source contracts and privacy/security in parallel. Required
integration and source-release gates follow [POLICY](../POLICY.md), with contributor
issue/PR templates and private security reporting described in the source.

Actual installation, independent GUI input, shared login, host changes and recovery
remain subject to [ACCEPTANCE](ACCEPTANCE.md). Publishing these specifications is
not evidence that those runtime scenarios have passed.
