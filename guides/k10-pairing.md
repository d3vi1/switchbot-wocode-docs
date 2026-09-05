# Re-pair a K10+ robot and barrel

You can use this guide to identify a robot and station, understand the intended association change, and distinguish a byte-level response from a repaired pair. The present release catalog does **not** enable the repair on real hardware: identity, address-order, two-device readback and persistence requirements remain open.

## What the investigation already establishes

In the analyzed Barrel Test 1.02 and normal Prod 1.04 paths, the extended setter `58 0A 02` copies six address bytes beginning at offset 6 of the outer mode-0 frame. The earlier Swift builder placed them at offset 5, a concrete encoding defect. The completed static trace shows that offset 5 is unused by this operation in both examined EXT handlers; a research encoder may emit `00` there as an explicit client convention. That does not establish the conversion from a QR/display MAC to the six protocol bytes.

The exact image digest, dispatcher and handler addresses are recorded in [the analyzed baseline](../reference/wocode.md#analyzed-baseline). This finding is static evidence, not a captured successful repair.

The handler echoes the copied bytes after status `01`. That echo alone does not show that the robot and barrel agree, or that the association survives a restart. Static analysis and qualification on devices are tracked separately.

The [detailed EXT58/EXT59 contract](../appendices/k10-barrel-ext58.md) records the exact guards, ignored byte, reply lengths and static storage findings. Its [synthetic fixtures](../fixtures/k10-barrel-ext58.json) are structural examples, not successful device captures. Test 1.02 has no `59/0A` peer getter. Prod 1.04 has a conditional getter whose complete mode-0 frame is `57 0F 59 0A 00 01`, after its state-dependent header gate accepts. The [production transport reference](../appendices/k10-barrel-prod104-ingress.md) ties that frame to the normal request characteristic and response submission, explains mode 1, and shows why a busy slot can discard a command despite a successful write callback. These are static findings, not successful hardware captures.

## Planned user procedure

1. Inspect and match both devices using [the identity guide](identify-your-devices.md).
2. Read both current associations before offering a paid change.
3. Confirm that the exact hardware and component versions have a qualified pairing procedure.
4. Show the requested before/after association and authorize the selected MAC pair.
5. Execute the documented writes in order, stopping on rejection, interruption or an unrecognized reply.
6. Read both associations again, reconnect, and verify the resulting state. Test persistence separately where the profile requires a restart.

The application reports verified, rejected, partially applied, interrupted or unknown outcome. A missing response must never produce a success face or a completed-repair message.

## Recover after an interruption

Reconnect to the same inspected devices and read their state before attempting another write. Do not blindly repeat a clear/unpair command: the first operation may have succeeded even if its notification was lost. If the state cannot be determined, retain an unknown result and provide the recorded steps for diagnosis.

The paired address on a third device is not implicitly cleared. A procedure that would affect another device needs its own explicit target and contract.
