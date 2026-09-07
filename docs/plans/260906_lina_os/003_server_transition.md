# VM development to physical-server installation

Status: design; physical installation and recovery remain unverified.
Parent: [Lina OS design](000_design.md).

## Confirmed destination

Development runs in a separate VM in the existing environment. The intended final
deployment replaces the physical server's OS with Lina OS. A desktop add-on is the
development delivery mechanism, not a reduction of the long-term OS goal.
Actual VM, disk, host-service and boot changes require an authorized target and
verified preservation/recovery plan.

## Development topology

Existing physical server → hypervisor → Lina OS development VM → agent desktops.

The VM contains the Omarchy baseline, chosen human account, Lina runtime, root executor,
and all desktop sessions. A `host` execution target inside this installation means the
VM's OS. It never resolves implicitly to the outer physical server. Host ID is created
inside the guest and remains explicit in every execution request.

Initial candidate if the environment supports it: KVM/QEMU with libvirt. This is a
proposal, not a verified installed capability. Inspect current virtualization support,
available resources, network and storage before provisioning. Start with virtual graphics
and software rendering; GPU passthrough is not needed to establish parallel input and
is not an initial dependency. Test real GPU compatibility separately before migration.

Provisional VM sizing for the experiment: 8 vCPU, 16 GiB RAM, 100 GiB system disk.
These are adjustable starting allocations, not minimum requirements or benchmark results.
Use a separate virtual data disk to rehearse persistence and reinstall behavior. Reserve
host capacity based on live workload measurements before selecting the actual allocation.

The guest can access an explicitly enrolled model endpoint over the network. It receives
neither the outer host root socket nor writable production disks by default. Reuse of real
data starts with selected copies. This makes automatic administration operate on the
intended development machine while production services continue normally.

Remote access reaches the guest's authenticated Lina gateway. Tailscale enrollment is
mandatory during onboarding; validate identity and app session handling rather than treating
network reachability as user authentication. Model endpoint access and desktop access
are separately configured connections.

## Server operating profile

The final OS must run without a human GUI login. Boot starts state mounts, executor,
runtime, computer manager and gateway. Omarchy's local graphical login remains available;
its physical desktop can be idle or absent while agent virtual desktops run.
Graphical login failure must not make the assistant control plane unavailable.

Server profile disables automatic suspend as an intended installation setting. Encrypted
boot requires a selected unlock method and a tested recovery path; neither auto login
nor service autostart solves disk unlock. Reboots are managed jobs with saved intent,
drained/paused tasks and post-boot reconciliation.

The GPU may serve other workloads. Validate virtual desktops using the final graphics
driver under representative concurrent server load. Do not reserve the entire physical
GPU for desktops without a measured need. Track idle and active desktop resource usage.

## Required migration inventory

Before writing a migration recipe, collect current evidence for:

- System/boot disks, UUIDs, mount units, storage pool/cache topology and recovery media.
- Persistent application databases, file shares, container volumes and service units.
- Network interfaces, addressing, remote-access enrollment and firewall configuration.
- GPU/kernel requirements and services competing for compute.
- Lina transcripts, memory, agent IDs, engine credentials and active jobs.
- Backup destinations, restore procedure and a successful restore drill.

Historical host notes are not a disk map. No device name, partition plan, pool topology
or destructive command is specified from recalled state. Preserve data disks under an
explicit reviewed device/UUID map when the actual installation is prepared.

## Transition sequence

1. Complete the two-agent VM acceptance matrix and produce a versioned installer recipe.
2. Rehearse new install plus application/data restore on a second disposable VM/disk set.
3. Capture live server inventory and map every retained service to a Lina OS deployment.
4. Rehearse graphics, storage drivers and cold boot on representative hardware where possible.
5. Prepare a concrete cutover plan: maintenance window, disk map, backups, restore proof,
   remote recovery access, health criteria and rollback decision point.
6. At the separately authorized cutover, stop source writers, take final consistent backups,
   install onto the designated system target, attach retained data and restore services.
7. Validate mounts and data integrity, network access, original service health, Lina identity,
   GUI parallelism, automatic host execution and cold-boot recovery before retiring old OS media.

Do not keep old and new runtimes concurrently writing the same Lina state or application
databases. Transferring installation identity and rotating host binding is an explicit
migration step; cloned VM identities must not cause jobs to target the wrong machine.

Rollback means restoring the former boot environment plus compatible application state.
An OS snapshot alone does not undo writes already made to retained data volumes. Keep
pre-cutover media and backups until the final validation window has passed.

## Additional acceptance gates

| ID | Scenario | Pass evidence |
| --- | --- | --- |
| S01 | Agent runs a root command in development | Only guest changes; outer host identity and state unaffected |
| S02 | Guest reboots without GUI login | Gateway, runtime and virtual desktops recover after disk unlock |
| S03 | New install restores data disk and state | Same agent/conversation identities; no unintended new sessions |
| S04 | Physical graphical session fails | Remote control plane and agent desktops remain usable |
| S05 | Existing workloads and desktops run together | Measured capacity, working GPU driver and healthy services |
| S06 | Cutover rollback rehearsal | Old environment opens compatible restored data successfully |

This extends the delivery roadmap with a physical-server qualification and migration
stage after 050. It does not replace the earlier backend experiment or skip its gates.
