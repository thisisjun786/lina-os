# Required Tailscale onboarding

Date: 2026-09-06. Status: product requirement; implementation pending.
Parent: [Lina OS design](000_design.md).

Tailscale is a required component of Lina OS. Onboarding cannot be marked complete
until this installation is enrolled and authenticated remote access is demonstrated.
This applies to Lina OS setup, not the first conversation of a standalone Lina
installation. It does not authorize changes to an existing host.

## User flow

1. Create the human owner account and establish internet connectivity.
2. Show “Connect Tailscale” with a short explanation: reach Lina from your other devices.
3. Start the supported Tailscale enrollment flow. The user signs into their own account
   and completes any required tailnet administration step.
4. Verify this OS installation is registered and connected. Development enrolls the
   guest VM as its own device, not merely the outer server.
5. Display the installation's verified remote Lina URL. Guide the user to connect a
   second device to the appropriate tailnet and open that URL.
6. Verify an authenticated request from that other device, load a conversation, and
   test the desktop streaming path when a desktop is available.
7. Record remote verification and complete onboarding once the remaining steps pass.

No “skip and finish” option. A user may pause onboarding and resume it later. Local
setup/recovery stays accessible when internet, enrollment or the second device is
unavailable; the product clearly remains in incomplete setup state.

## State and completion

Track not-installed, service-unavailable, sign-in-required, awaiting-enrollment,
connected, remote-verification-pending and verified. These are proposed Lina states,
not claimed Tailscale API enum values. Persist progress without login URLs, auth keys
or other enrollment secrets in ordinary logs or the installation manifest.

Completion requires the actual local daemon/device state plus a scoped verification
challenge redeemed through the remote authenticated gateway from a different enrolled
device. A localhost request, package install or generated URL is not sufficient proof.
The exact device-identity verification method requires current Tailscale API research.

Separate first-install completion from ongoing connection health. Later connectivity
loss shows an actionable state and permits reconnection without resetting agents,
conversations or restarting the onboarding wizard. Do not stop local jobs solely because
remote access is temporarily unavailable. Reinstallation/cloning must enroll a distinct
device or follow an explicit identity migration, never blindly duplicate node state.

## Access contract

Remote Lina access is private to the intended tailnet and authenticated owner/session.
Enrollment does not automatically grant every tailnet member administrative control.
No public internet exposure, subnet routing or exit-node function is implied by this
requirement. Application identity and desktop input ownership remain enforced.

The implementation experiment must select and verify the supported HTTPS exposure
method, WebSocket streaming, device identity mapping and relevant tailnet policy. Do
not assume a particular Serve command, DNS configuration or certificate arrangement
before checking current official documentation and the test tailnet.

## Acceptance additions

| ID | Scenario | Required result |
| --- | --- | --- |
| T01 | Tailscale installed but not enrolled | Onboarding remains incomplete |
| T02 | Enrollment pending or network unavailable | Clear state; resumable local setup |
| T03 | Guest enrolled, only localhost tested | Remote verification still pending |
| T04 | Owner connects from another enrolled device | Conversation loads; challenge verifies |
| T05 | Remote computer view and control transfer | Streaming and ownership gate work remotely |
| T06 | Another tailnet member requests access | No implicit owner/admin grant |
| T07 | Connection lost after completion | Reconnect guidance; local jobs/state retained |
| T08 | VM cloned or physical server installed | Device identity handled explicitly |

Apply these gates to delivery stages 030/040 and to the physical-server transition.
This document is a design specification, not evidence of a working remote connection.
