# Production 1.04: from a BLE write to an EXT response

This page lets you construct complete research frames, interpret the returned bytes, and see why a successful BLE write is insufficient to establish a repaired pair. It describes the normal application service in one exact K10 barrel image. It does not enable a hardware repair procedure.

The image is `WoSweeperMiniBarrel_app_prod_V1004.bin`, SHA-256 `997788eedfa24ddf4b7d7c082b9b8994578296c437c3b11802224f957c5cb219`. The [corpus](../corpus/firmware-inventory.json) identifies those bytes; the [ingress contract](../contracts/k10-barrel-prod104-ingress.json) and [synthetic examples](../fixtures/k10-barrel-prod104-ingress.json) describe this analysis in structured form. Existing set, clear and getter state rules are in [the handler reference](k10-barrel-ext58.md).

## The normal application service

Registration selects this path when bootstrap helper `0x00812934` returns a value other than 2. The alternative result-2 service profile remains untraced. In the normal path, registration at `0x00812694` supplies callback pointer `0x00811EAD` to wrapper `0x00816314`. The pointer's low bit denotes Thumb code; the callback body begins at `0x00811EAC`.

The wrapper registers the attribute table at `0x008175F8` through ROM service registration at `0x0004F66E`, stores the callback pointer at `0x002082CC`, and returns a service identifier. Registration stores that identifier at `0x00208AAD`; the application callback checks the same location. The table contains six 28-byte records, or 168 bytes.

| Attribute | Purpose | UUID or declaration |
|---:|---|---|
| 0 | Service | `CBA20D00-224D-11E6-9FB8-0002A5D5C51B` |
| 1 | Write characteristic declaration | Properties `0C` |
| 2 | Application request value | `CBA20002-224D-11E6-9FB8-0002A5D5C51B` |
| 3 | Notification characteristic declaration | Properties `10` |
| 4 | Application response value | `CBA20003-224D-11E6-9FB8-0002A5D5C51B` |
| 5 | Notification configuration | CCCD `2902` |

The request attribute's permission word is `00000010`. Its declared bits do not request attribute-level authentication or encryption. This table fact does not prove runtime link admission, eliminate the application mode gate, or establish that a notification is enabled.

## Admission and staging

Write callback `0x008163B4` requires attribute index 2 and a non-null value pointer. It returns `040A` for the wrong attribute and `040D` for a null value. These are callback results, not WoCode response bytes. It forwards write type and the declared 16-bit length without checking them locally.

The callback forwards an event containing connection at byte 0, type `03` at byte 1, selector `01` at byte 4, write type at byte 5, length at bytes 6–7, and the value pointer at bytes 8–11. Application callback `0x00811EAC` requires the registered service identifier, those event markers, and an empty pending slot.

The staging block starts at `0x002080CF`: pending is byte 0, connection is byte 1, stored length is byte 2, and the frame starts at byte 3. For an admitted event the callback clears 247 frame bytes, copies the declared data, stores the connection and low eight bits of length, marks the slot pending, and signals semaphore `0x002092A4`.

**When the slot is busy, the new frame is not copied even though the write callback returns zero.** A callback success or accepted ATT write therefore cannot prove that the command reached the dispatcher.

The copy count is a 16-bit event length, the copy index is eight bits, and only the low length byte is retained. No explicit local minimum or maximum check was found in this callback/staging path. The 247-byte clear is not a demonstrated safe maximum request length. Stack ATT/MTU limits and long-write handling remain untraced; these facts do not prove that arbitrary large writes are admitted.

Short frames are also not made valid by missing firmware guards. The host minimums below supply every byte accessed by their respective operation. If the traced staging path admits the old 11-byte setter, its cleared buffer supplies a zero after the five shifted peer bytes; this is a conditional static result, not a tested request.

## Complete-frame dispatch

The worker waits at `0x00816BE8` on the same semaphore. Its call at `0x00816C0E` invokes dispatcher **`0x00810D28`** with the staged frame pointer, the stored length, a response buffer and a deferred-callback slot. Its EXT tail branch at `0x00810E34` reaches handler **`0x00810950`**. Older propagated function names were not reliable evidence for this connection.

Let **F** be the complete frame and **P** start at the EXT family byte. After accepted mode 0, P = F + 2; after accepted mode 1, P = F + 6. The original request length is not forwarded into the EXT handler. The dispatcher does not check a minimum length before reading F[0] and F[1].

F[0] must be `57`; another value produces response length zero. Nonzero upper two bits of F[1] produce one-byte `04`. This contract covers EXT class `F[1] & 0F == 0F`; it does not inherit the dispatcher's separate exception for class `0A`.

## Mode selection and the four-byte check

Configuration starts at `0x00207FC0`. Define **a** as byte `+10` bit 7 and **b** as byte `+11` bit 5, with hexadecimal offsets. Instructions beginning at `0x00810D58` establish the unsigned sum **s = a + b**.

| EXT mode | Admission | P offset | Rejection body |
|---:|---|---:|---|
| 0 | a equals b; equivalently s is 0 or 2 | F + 2 | `07` if s is 1 |
| 1 | s is 0, or all four comparison bytes match | F + 6 | `09` otherwise |
| 2 | Rejected | — | `0A` |
| 3 | Rejected | — | `0A` |

Helper `0x008102AC` compares F[2..5] byte-for-byte with configuration bytes `+4..+7`, returning 1 only if all four match. Its older address-related name was misleading. This establishes equality, not the value's provisioning, secrecy or user-visible meaning. In particular, when a and b are both 1, mode 0 is allowed but mode 1 still requires equality. When both are 0, mode 1 bypasses the comparison result.

The fixtures cover all four flag combinations and both mode-1 comparison outcomes, plus independent mismatches at each of the four check positions. These rules are proven for this production image; they do not expand the separately recorded Test 1.02 evidence scope.

## Complete research layouts

`<check4>` denotes the four comparison bytes. `<peer6>` denotes explicit protocol bytes, whose conversion from a QR/display address remains unverified. A zero ignored byte is a client convention, not a captured vendor value.

| Operation | Mode 0 | Mode 1 | Host minimum, mode 0 / 1 |
|---|---|---|---|
| Set | `57 0F 58 0A 02 <ignored> <peer6>` | `57 1F <check4> 58 0A 02 <ignored> <peer6>` | 12 / 16 bytes |
| Clear | `57 0F 58 0A 01` | `57 1F <check4> 58 0A 01` | 5 / 9 bytes |
| Getter | `57 0F 59 0A <ignored> 01` | `57 1F <check4> 59 0A <ignored> 01` | 6 / 10 bytes |

The setter ignores F[5] in mode 0 or F[9] in mode 1, then copies six bytes from F[6..11] or F[10..15]. The getter ignores F[4] or F[8]; its required `01` is at F[5] or F[9]. These are host obligations derived from byte accesses, not firmware-enforced exact lengths.

For example, after the mode-0 gate accepts, the complete synthetic getter frame is `57 0F 59 0A 00 01`. With stored peer `12 34 56 78 9A BC`, local source bytes `22 33 44 55 66 77`, and the getter's state predicate true, its response is exactly:

```text
01 20 01 12 34 56 78 9A BC 77 66 55 44 33 22
```

The [handler predicate](k10-barrel-ext58.md#read-behavior-differs-by-firmware) remains required. A false predicate returns only `01`. The example is original synthetic data, not a capture or a device address mapping.

## Response initialization and submission

After header and mode acceptance, `0x00810D8A` initializes response byte 0 to `01` before opcode dispatch. Thus unsupported `58/0A` operations such as `00` or `03` return exactly one byte `01` in Prod 1.04 and do not mutate pairing state. An otherwise out-of-length write to response byte 1 does not become part of that returned body.

The worker forwards the response buffer and dispatcher-returned length through `0x00816C2A → 0x00816464 → 0x0004F7A4`, using the saved connection, registered service and attribute index 4. The wrapper uses PDU selector 0 (`GATT_PDU_TYPE_ANY`) on the notification-only declared attribute. **It adds no WoCode frame prefix on this path.** The set response remains seven bytes `01 + peer6`; the conditional getter response remains 15 bytes, or one byte if its predicate fails.

This closes the static path to notification submission. It does not establish CCCD state, stack acceptance, actual notification delivery or response correlation on a device. An application still needs those transport checks and must not treat submission as a completed operation.

## What remains before a repair can be enabled

QR/advertisement mapping, reciprocal association readback, reconnect behavior, deferred storage completion and persistence remain unresolved. The alternate service profile and runtime security/ATT admission also need separate evidence. The [release catalog](../catalog/capabilities.json) remains empty. This newly traced connection improves the documentation; it is not a new firmware API change or a hardware qualification.
