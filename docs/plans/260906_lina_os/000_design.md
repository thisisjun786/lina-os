# Lina OS: autonomous host and agent desktops

Date: 2026-09-06. Status: design v0.2, proposed; not implemented or deployment-approved.

## Product contract

Install an Omarchy-based personal workstation, create the human account (for example
`alex`), and provide Lina as its persistent assistant. Agents operate the host with
automatic execution and each has an independently controllable remote desktop.
The human can keep using their own desktop, observe any agent, take control, and
return control without replacing that agent's conversation or memory.

Product requirements:

- Omarchy is the desktop foundation; Lina owns the assistant experience.
- Agent system operations use automatic approval by default, including privilege
  elevation. There is no mandatory per-action human approval queue in this product mode.
- Human identity, agent identity, and desktop session identity are distinct.
- Agents perform actual GUI automation, not just terminal or browser-only work.
- One human login to a website should be reusable by existing and newly created agents.
  Agent creation must not itself require signing into the same services again.
- Preserve parallel work wherever feasible. Reauthentication is for service expiry or
  additional authentication challenges, not a routine per-agent setup step.
- Tailscale enrollment is mandatory during onboarding for remote access. Installation
  alone is insufficient; verify registration and an authenticated remote connection.
- A working model configuration is also mandatory. Present Codex first, Ollama Cloud
  second and local inference third. Codex and Ollama Cloud are first-class Lina integrations.
- OpenCodex is a required installed tool, with service readiness included in setup.
  Mandatory installation does not imply every model request must use its proxy.
- OmO Native is a required installed development tool with its own lifecycle.
  Any future coding-job integration must preserve Lina conversation, identity
  and memory ownership.

Develop in a separate VM first, then qualify installation on a selected physical
server as the long-term target.
Working assumptions: one human owner per installation; two concurrent agent desktops
initially. Hardware sizing is unmeasured.
Additional human tenants are outside v0.1. Multiple agents are in scope from the start.

Document map:

- [Runtime contracts](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/001_runtime_contracts.md): records, actions, control transfer, recovery.
- [Delivery and acceptance](002_delivery.md): repository changes, experiments, acceptance gates.
- [VM development and server transition](003_server_transition.md): guest boundary, boot and migration.
- [Required Tailscale onboarding](004_tailscale_onboarding.md): enrollment and remote verification.
- [Required model onboarding](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/005_model_onboarding.md): provider order and local qualification.
- [Required OpenCodex tool](006_opencodex.md): installation, readiness and routing boundaries.
- [Required OmO Native tool](007_omo.md): development delegation and installation lifecycle.

## Product and OS ownership

[Lina](https://github.com/thisisjun786/lina) owns agent identity, conversations,
memory, Codex task execution and computer contracts. Lina OS composes the pinned
product with the OS, desktop manager, local host executor and installation lifecycle.
Use [modules.json](../../../modules.json) for the selected source revision and module
profiles. A source revision is not an installable OS artifact.

The runtime uses Codex and OpenCodex. Retired Senpi and OmO job packages are not
required dependencies. OmO Native remains an independently installed development
tool; any future product adapter needs an explicit contract and compatibility test.
No mandatory external memory service is introduced by this design.

Moving a runtime to an OS service requires explicit credentials/configuration
enrollment and state import. A service UID must not assume access to the human home.

## Deployment shape

| Component | Runs as | Responsibility |
| --- | --- | --- |
| Omarchy physical desktop | human UID, e.g. alex | Human applications and local Lina launcher |
| Lina runtime | stable service UID `lina-runtime` | Existing agent fleet, memory, durable jobs, policy |
| Desktop manager | managed service | Allocate/reconnect independent desktops and map agent IDs |
| Agent desktop | execution UID strategy pending experiment | Apps, session settings and virtual input |
| Host executor | root service, local Unix socket | Execute host commands under requested user/root identity |
| Web gateway | unprivileged service | Authenticated UI, event stream, desktop streaming proxy |

Per-agent Linux accounts are not a product requirement. Start by evaluating a shared
execution UID with separate display/session settings. Use distinct internal UIDs only
if app/session collision evidence justifies them; this must not add per-agent website
login steps. Persist any selected identity mapping. Every agent has the same right to
request host administration. UIDs are not a security boundary against root-capable agents.

Initial topology: runtime and desktops run on the same always-on machine. A later
remote desktop backend can keep the same computer/action contract. Turning off or
suspending this machine stops local progress; remote viewing does not provide compute.

## Desktop backend decision

Primary candidate: independent X11 desktop sessions with KasmVNC. Each computer has
its own display, input state, session bus, app processes and persistent home. The
physical Omarchy session remains Hyprland. This avoids depending on concurrent input
isolation inside the human compositor.

This is a conditional choice: Arch packaging, desktop startup, Korean input, rendering
and browser embedding must pass the experiment in 002. Verify display instances
and browser access against the pinned KasmVNC release; the experiment must
establish this exact Omarchy combination.

Fallback candidate: persistent desktop containers with KasmVNC and explicit host
execution. This adds image/root-filesystem persistence work and a host/container target
distinction. A container is not called a VM and its root is not host root.

Wayland sessions plus wayvnc remain a later backend candidate. A virtual output alone
does not prove independent keyboard focus or compatibility with current Hyprland.
Per-agent VMs are reserved for workloads needing a different OS/kernel; they are not
required just to provide multiple screens. No implementation choice silently narrows
the product to browser tabs or replaces GUI tasks with terminal-only automation.

## Full autonomous execution

The installer records an explicit `autonomous-host` product profile. Agent tool requests
execute without interactive approval, subject to target validity, lifecycle state,
resource scheduling and user stop. A resource queue is not an approval queue.

The host executor accepts arbitrary executable/argv or explicit shell-script requests
from the authenticated runtime, with host ID, run ID, cwd, execution UID and resource
claims. It can run as root. Structured helpers cover package/service/file operations;
general shell remains available for operations outside those helpers.

The model-facing runtime and remote browser are not root processes. Only enrolled local
runtime peers can call the root socket. Remote clients authenticate to the gateway;
screenshots, web pages and untrusted plugins cannot directly submit root RPC requests.
This is endpoint access control, not a human confirmation requirement.

Codex configuration, tool adapters, OS rights and provider behavior all affect execution.
The installed profile must explicitly configure supported native rules and verify no
second Lina approval layer remains. Existing native mode must not be relabeled as
unconditional automatic approval. Provider-imposed refusals or confirmation requirements
remain possible and must be reported rather than advertised away.

All general host mutations take a conservative host mutation lock initially. Known
disjoint file jobs may later use narrower locks. Package manager, service updates,
power operations and Lina self-updates are serialized. Root access means a determined
agent can circumvent cooperative locks; this design does not promise enforcement
against agents intentionally using their full administrative authority.

## Browser identity and shared work

The required experience is one login reused by multiple agents, including agents
created afterwards, with as much parallel work as possible. Profile topology,
Linux UID topology and authenticated-session ownership remain open. A per-agent
login or globally serialized desktop is not the assumed baseline.

Evaluate managed shared browser ownership with agent-assigned work surfaces, and compare
it with exclusive desktop handoff. The former is a research candidate, not an established
implementation: independent visible screens, input focus and shared authentication must
be demonstrated together. Do not infer this from separate tabs or API-only automation.

Exclusive handoff remains a fallback candidate: one persistent signed-in desktop is
borrowed by agents in turn. Measure its queueing cost before proposing it as the baseline.
Do not silently accept global serialization or per-agent re-login to simplify implementation.
If the combined requirements cannot be met, return the evidence and explicit tradeoff.

Do not open one live Chromium user-data directory from multiple browser processes.
Session reuse must use a supported ownership mechanism, not assumed cookie copying.
Service-imposed session expiry and extra authentication remain possible; one-login reuse
is an onboarding requirement, not a guarantee that websites never request authentication.
Shared files retain an explicit workspace and ownership policy independently of logins.

Agent removal archives its own state and detaches its computer; shared authentication
must survive removal of an individual agent. Computer stop, computer
reset, profile deletion and agent deletion are distinct operations. Idle desktops may
stop only under an explicit policy; default v0.1 retains running apps after viewer close.

## Computer use and remote viewing

Lina tools select a bound computer, capture a frame, execute mouse/keyboard actions,
and return a new frame or result to the existing agent loop. Screen metadata includes
pixel dimensions, scale, display generation and frame identity. Normal actions remain
local; model calls receive the images needed for reasoning.

Human viewing uses KasmVNC's browser client behind the gateway. It is a separate data
path from model screenshots. Do not assume KasmVNC is standard RFB/noVNC compatible.
Agent injection uses a dedicated per-display input driver; it does not depend on a
human viewer being connected. Both human and agent writes pass the same ownership
gate. The browser must not retain a direct writable VNC path after surrendering control.

The host's physical desktop can be exposed as an additional computer later. It has one
input owner and therefore cannot be shared concurrently with the human's mouse. Independent
agent desktops are the default work location; full system management remains available
through host execution even when physical desktop control is unavailable.

## Installation, persistence and updates

Installer stages: inspect selected target; install/pin Omarchy baseline; create chosen
human account; install Lina packages/internal identities; enroll provider configuration;
initialize state; start services; pair local UI; run acceptance probe. Each stage records
completion and supports rerun without recreating accounts or overwriting existing state.
Actual disk selection/formatting belongs to a future install task, not this design.

Product data uses `LINA_HOME`. Other locations below are proposed OS-owned paths:

| Path | Contents |
| --- | --- |
| `/etc/lina-os/installation.json` | Install ID, owner UID/name, backend/version choices |
| `LINA_HOME` (default `~/.lina`) | Product-owned conversation, memory and configuration |
| OS-managed computer state (location pending) | Persistent home/profile and desktop metadata |
| OS-managed action journal (location pending) | Host/computer receipts linked to Lina task identity |
| `/srv/lina/shared/` | Shared work files with managed group ownership |
| `/run/lina/` | Private runtime sockets and transient state |

Credentials live in a restricted, enrolled engine directory, not installation.json,
browser responses or generic action logs. The onboarding order is Codex, Ollama Cloud,
then local inference, using Lina's integrated provider paths. OpenCodex is a required
installed tool; per-provider routing remains a separate integration decision.
Compatibility with vision and tool schemas
requires a probe, not catalog presence. Existing native credentials and live model defaults
are not silently changed. Configured and tested routes are recorded separately.

System units start after required state volumes are available and do not require GUI
login. Network/provider unavailability leaves local state accessible and jobs queued.
Encrypted disk unlock still precedes services; unattended boot is not promised without
a separately selected and tested unlock arrangement.

Updates stage a versioned release, drain managed work, checkpoint durable state, switch
the application release, then check health. OS package upgrades use the host job queue.
Memory/transcript databases are backed up consistently; browser profiles require a
quiesced backup. Filesystem snapshots do not reverse external website submissions and
do not automatically preserve running processes. Destructive schema migrations need a
compatible backup/restore plan; old binaries must not open an incompatible new schema.

## Unresolved deployment choices

- Development VM and eventual selected physical-server install are product requirements;
  exact VM resources, GPU and boot/unlock arrangement require measurement.
- Exact Omarchy/KasmVNC versions and Arch build route: resolve by packaging experiment.
- Model route passing real screenshot/action tests: resolve with authorized provider test.
- Shared authentication with parallel work is a required feasibility investigation;
  profile/UID topology and unavoidable serialization boundaries remain undecided.
- ISO distribution, signing and release channels: follow successful install-profile prototype.

## Public sources

Consult current, pinned upstream documentation before choosing a backend. These
references do not establish Lina OS compatibility or completed runtime verification.

- [Omarchy manual](https://omarchy.org/manual/): Arch, Hyprland, Quickshell foundation.
- [Omarchy AI](https://omarchy.org/manual/ai/): default agent launch and automatic modes.
- [Grok Bot FAQ](https://docs.x.ai/grok-bot/faq): shared computer and per-bot screens;
  underlying compositor/streaming implementation is not established by this page.
- [KasmVNC](https://github.com/kasmtech/KasmVNC): web desktop, multiple display instances,
  custom protocol; use pinned-release documentation when implementing.
- [wayvnc](https://github.com/any1/wayvnc): headless Wayland capture and virtual input.
- [Chromium user data](https://chromium.googlesource.com/chromium/src/+/main/docs/user_data_dir.md):
  running browser instances cannot share one user data directory.
- [Computer-use loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool):
  application executes model-requested actions and supplies screenshots.
