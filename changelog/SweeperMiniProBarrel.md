# SweeperMiniProBarrel: BLE API changes

Scope: the internally named `WoSweeperMiniBarrelPro` test images below. The name-order aliases `SweeperMiniProBarrel` and `SweeperMiniBarrelPro` are reconciled by image hash; this does not qualify arbitrary marketed Pro hardware.

## 2026-09-05 — `barrelpro-test105-test106`

**Evidence:** static comparison with independent checks of the EXT and basic-information handlers. No BLE capture or complete app-facing GATT admission proof accompanies this entry.

| Comparison member | SHA-256 |
| --- | --- |
| `WoSweeperMiniBarrelPro_app_test_V1005.bin` | `b7d8d880349cada3869988aa3b32d986f779896b0743d3022883a59d4114d3e4` |
| `WoSweeperMiniBarrelPro_app_test_V1006.bin` | `e5f5d03e707f9d816e1a5e9cbf53546cc91cb81eeb9beb006352a207750b3b6a` |

No added or removed selector, reply-layout change or mode-gate change was found in the reviewed EXT `22`, `23`, `58` and `59` paths. `5A` and `5B` remain unimplemented fallthroughs in that dispatcher. This statement covers the inspected paths only, not every firmware function or physical behavior.

The concrete differences found are diagnostic reply **values**, with their request and response shapes unchanged:

| Mode-0 request | Test 1.05 result body | Test 1.06 result body |
| --- | --- | --- |
| `57 00 03 00` | `01 01 05` | `01 01 06` |
| `57 00 03 01 00` | `01 00 07 E8 04 12 10 04 2B` | `01 00 07 E8 04 12 10 14 0C` |

These are statically derived result bodies, not captured notifications. The first row reports firmware version; the second reports build information without assigning a timezone. Header/state admission still applies.

## Shared Pro behavior relevant to client compatibility

Both Pro images accept `58/0A/02` by copying six raw peer bytes at payload offsets 4–9, then overwrite result byte 1 with `01`. For peer bytes `A0 A1 A2 A3 A4 A5`, the seven-byte body is therefore `01 01 A1 A2 A3 A4 A5`. The non-Pro exact-six-byte echo contract must not be generalized to these images. This is a shared Pro-versus-non-Pro difference, **not** an API change introduced by Test 1.06.

Both Pro clear branches perform their clear/queue work unconditionally once that branch is reached. Their conditional `59/0A` getter also has an extra state-byte gate relative to the reviewed non-Pro production image. Its field meaning is not established here. Neither acknowledgment establishes persistent pairing or actual actuation.

The basic-information handler is `0x00810E84` in both images; the EXT dispatcher is `0x008109E8`. Complete frame dispatchers are `0x00810F64` (1.05) and `0x00810F68` (1.06). The instruction at `0x00810BEA` stores `01` into result byte 1 in both EXT handlers. Equal or shifted addresses are navigation aids, not changes in API semantics.

See [the detailed comparison evidence](../appendices/barrelpro-test105-test106.md). These findings do not enable Pro repairs in the application catalog.
