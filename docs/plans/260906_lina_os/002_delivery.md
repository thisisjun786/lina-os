# Delivery and acceptance

Status: design roadmap, not an executable patch plan or authorization to install.
Parent: [Design](000_design.md); [Contracts](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/001_runtime_contracts.md).

## Boundary decision

Lina owns the agent loop, durable task and computer contracts, memory and connection
UI. Lina OS owns desktop processes, drivers, streaming services, host privilege and
installation. Register computer tools through the existing Codex runtime boundary.
Keep OS process management separate from model adapters and persona state; do not
introduce a second assistant loop.

## Proposed change map

These are ownership targets, not a claim that the packages or APIs already exist.
Select exact source paths against the pinned Lina version during implementation.

| Owner | Responsibility |
| --- | --- |
| Lina core | Computer/run/action/lease contracts and domain transitions |
| Lina runtime and Codex adapter | Existing-session tools, agent bindings and durable task results |
| Lina web | Authenticated computer view, stream proxy and control transfer UI |
| Lina OS desktop manager | Desktop lifecycle, journal, per-display driver and streaming |
| Lina OS host executor | Local authenticated privilege and durable host-action receipts |
| Lina OS installation | Versioned manifest, units, build definitions and recovery |
| Both repositories' tests | Consumer contracts plus real owned-guest GUI/boot probes |

Preserve existing transcript/memory formats. Data migration is an explicit operation,
not a side effect of installing an OS profile. Product runtime sources stay in Lina.

## Dependency-ordered work

### 010: Desktop feasibility experiment

On a separate selected Omarchy VM/PC, pin actual versions and build/install the chosen
KasmVNC route. Start two desktops with separate session buses; compare shared execution
UID with separate UIDs if app collisions arise. Browser profile topology remains open.
Run a browser and a document app on each. Use simultaneous, distinguishable typed
markers to prove input isolation while the human uses the physical desktop.

Verify capture, mouse, Korean/ASCII text, scaling, browser streaming, viewer disconnect,
logout and service restart. Test headless boot independently from login. Record CPU/RAM
and streaming latency under two active desktops. No model calls are needed for this step.
If native Arch packaging fails, evaluate the container backend against the same tests
and record the additional persistence/host integration cost before selecting it.

Before selecting the baseline, sign into a test website once, create another agent,
and verify reuse without another login. Compare parallel authenticated work surfaces
with serialized handoff; record focus collisions and waiting time. A shared profile
folder or separate tabs alone is not proof of independent GUI control. Account creation
and provider calls remain outside this documentation task.

Exit: reproducible recipe and real evidence, or a named backend blocker. No claimed
Lina integration or autonomous reasoning from a working VNC screen alone.

### 020: Durable computers and input ownership

Implement core contracts, computer manager and journal. Start with a failing competing
writer test; cover transfer timeout, expired epoch, display restart and action replay.
Use controllable signals/fake clocks in tests, never sleep-based race assertions.
One agent defaults to one bound computer; shared computers use the same lease machinery.

Exit: two real desktops, one writer each, forced stale actions rejected, persistent
bindings recovered without new agents or new conversations.

### 030: Lina tools and remote Computer view

Inject screenshot/input tools into the existing session, map frames to correct displays,
and embed authenticated viewing/control in lina-web. Verify model route image/tool
compatibility with a real bounded task only when provider execution is authorized.
Prove stop and takeover reach the actual driver; an attractive UI alone is insufficient.

Exit: ask each of two agents to operate a different GUI app, observe both, take over
one, return it, and receive durable results in the original conversations.

### 040: Host administration and installation profile

Implement full-access host executor, root/socket identity checks, serial host mutations,
automatic policy configuration and install manifest. Test selected owner name other
than the developer. A harmless temporary-file command running as root proves elevation; an SDK
permission-unit test alone does not. Test unauthenticated socket/gateway callers too.

Exit: agent installs a test package or manages a disposable service on the test host
without approval prompts; target host and resulting state are proven. A container-only
mutation does not count as host administration. Preserve human desktop continuity.

### 050: Shared login, restart and update recovery

Use a dedicated test account with the backend selected in 010. Human logs in once;
agent A works, then a newly created agent B reuses authentication without another login.
Exercise simultaneous work and prove which resources, if any, require serialization.
Test queued simultaneous requests, app restart, host reboot, uncertain action and
duplicate completion delivery. Exercise staged update and compatible rollback.

Exit: an installable prototype satisfying the matrix below. Custom ISO production,
signing, release automation and deployment to an existing operational host remain
separate work; the prototype includes the entire agent desktop/host behavior.

## Acceptance matrix

| ID | Scenario | Pass evidence |
| --- | --- | --- |
| A01 | Install with owner `alex` | No developer-specific paths; login and runtime ready |
| A02 | Two agents plus human type concurrently | Distinct text lands only in intended apps |
| A03 | View computer without taking over | Observation sends no input and steals no lease |
| A04 | Take over during queued agent input | Old epoch fenced; no late click after grant |
| A05 | Return control after navigation/resize | Agent uses fresh frame and correct coordinates |
| A06 | Close browser viewer | Agent completes and result appears after reconnect |
| A07 | Restart agent desktop | Same profile and conversation; old generation rejected |
| A08 | Crash after external action before receipt | Uncertain action is inspected, not replayed |
| A09 | Automatic host administration | Actual host state changed without approval prompt |
| A10 | Two package/update jobs overlap | Ordered dispatch and separate durable receipts |
| A11 | One login, then create agent B | B reuses authentication without signing in again; no live-profile race |
| A19 | Two authenticated tasks in parallel | Measured concurrency and input isolation; unavoidable queues explicitly documented |
| A12 | Unauthenticated remote input/root request | Rejected; auto approval does not expose the endpoint |
| A13 | Duplicate events/results | One visible result; no repeated command |
| A14 | Reboot with encrypted disk | Unlock requirement documented; services recover afterwards |
| A15 | Provider outage or unsupported vision | Accurate unavailable state; no fake successful action |
| A16 | Update fails after new schema installed | Compatible recovery, no old writer on new schema |
| A17 | Capacity exhausted | Jobs queue; profiles retained; human UI responsive |
| A18 | Agent archived | Desktop/profile retained until separately removed |

Implementation checks follow each repository's current policy and executable CI.
Use the [OS source checks](../../CI.md) for this repository and Lina's own checks
for product changes. Browser login persistence, GUI input, privileges and reboot
recovery require the actual disposable environment in addition to unit tests.
Record hardware, component revisions and observable results.

This roadmap defines the complete intended behavior. Exact installation recipes
follow the feasibility experiment; no OS implementation is claimed by this document.
