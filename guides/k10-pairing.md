# Re-pair a K10+ robot and barrel

The intended operation associates one inspected K10+ robot with one compatible auto-empty station. The present release catalog does **not** enable this repair on real hardware: the investigation is still closing identity, address-order, two-device readback and persistence requirements.

## What the investigation already establishes

In the analyzed Barrel Test 1.02 handler, the extended setter `58 0A 02` copies six address bytes beginning at offset 6 of the outer mode-0 frame. The recovered Swift builder puts them at offset 5. This is a concrete encoding defect; appending an assumed zero is not a substitute for understanding the intervening byte and address representation.

The exact image digest, dispatcher and handler addresses are recorded in [the analyzed baseline](../reference/wocode.md#analyzed-baseline). This finding is static evidence, not a captured successful repair.

The handler echoes the copied bytes after status `01`. That echo alone does not show that the robot and barrel agree, or that the association survives a restart. Static analysis and qualification on devices are tracked separately.

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
