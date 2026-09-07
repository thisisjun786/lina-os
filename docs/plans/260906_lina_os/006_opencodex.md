# Required OpenCodex tool

Date: 2026-09-06. Status: mandatory inclusion planned; integration details pending.
Parent: [Lina OS design](000_design.md).

OpenCodex is part of the required Lina OS toolset alongside Tailscale and a working
model configuration. The installer provisions a pinned version, manages its lifecycle,
and exposes an entry in system settings.
This document does not authorize changes to the existing host's OpenCodex installation.

## Scope

- Include OpenCodex in the installation manifest and update/rollback inventory.
- Verify its supported local management/service interface is ready during setup.
- Integrate provider/catalog management where supported by the pinned release.
- Keep Codex → Ollama Cloud → local as the model onboarding presentation order.
- Determine routing per integration; mandatory tool installation is not mandatory
  proxying of every model call. Preserve working direct routes where needed.
- Preserve the current installation's saved providers and model defaults.

Use the configured catalog and actual supported endpoints when implementing. Do not
assume API shapes, ports, sign-in forwarding or tool/image compatibility from the tool
name. Shared credentials remain with their configured owner; avoid creating duplicate
sign-in requirements merely because OpenCodex is installed. Resolve that ownership in
the provider integration phase, not by silently copying credential files.

## Setup and lifecycle

Provision OpenCodex before the provider selection screen needs it. Install and service
readiness are separate from successful provider authentication/inference. Record each
state separately. An unavailable required service leaves setup resumable and incomplete.
After setup, an OpenCodex outage affects routes that depend on it; direct routes and
local conversation history need not stop. Show the actual dependency failure.

In development, provision inside the Lina OS VM, with distinct configuration and service
identity. Do not reconfigure the outer server's existing process or ports. Any connection
to an existing remote OpenCodex instance is explicit enrollment, not implicit discovery
and reuse. Physical-server migration handles identities, credentials and data separately.

Remote management, if exposed, follows the Tailscale/owner access contract. A management
UI URL and a model API endpoint are separate integration surfaces. No public exposure
or sharing of owner credentials is implied by mandatory inclusion.

## Acceptance additions

| ID | Scenario | Required result |
| --- | --- | --- |
| O01 | Fresh installation | Pinned OpenCodex installed and local service readiness verified |
| O02 | Provider selection | Requested order retained; no redundant mandatory sign-in |
| O03 | Proxy capability unavailable | Explicit route decision, no falsely claimed compatibility |
| O04 | Development VM setup | Outer server installation unchanged |
| O05 | OpenCodex outage | Dependent routes report failure; independent routes remain available |
| O06 | Upgrade/restart | Configuration retained and service readiness restored |

Integrate this work into delivery stage 040. Exact packaging, lifecycle commands and
credential ownership are cxc implementation-planning decisions backed by current code.
