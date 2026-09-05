# SweeperMiniBarrel: BLE API changes

Product scope: K10+ barrel. These are reviewed comparisons, not a declared firmware upgrade sequence.

## 2026-09-05 — `barrel-ext59-0a-test102-prod104`

**Evidence:** static EXT-handler comparison, independently reviewed. No real BLE capture or hardware qualification accompanies this entry. Complete GATT admission and the Prod 1.04 outer-frame dispatcher remain unresolved, so this entry describes the API-handler delta without claiming a working phone-to-barrel procedure.

| Comparison member | Channel | SHA-256 |
| --- | --- | --- |
| `WoSweeperMiniBarrel_app_test_V1002.bin` | Test 1.02 | `0227cd90a7147c62985bc8a4080157e010b14e8a4ed69f7c2632535ae49479c5` |
| `WoSweeperMiniBarrel_app_prod_V1004.bin` | Production 1.04 | `997788eedfa24ddf4b7d7c082b9b8994578296c437c3b11802224f957c5cb219` |

Both reviewed EXT handlers begin at `0x00810950`; equal addresses alone are not the evidence—the bodies were inspected independently. Let `P` begin at the EXT family byte (`58` or `59`).

| API behavior | Test 1.02 | Production 1.04 | Client impact |
| --- | --- | --- | --- |
| `59 0A` address result | No selector `0A` branch; returns one-byte `01` without address data | When `P[3] == 01 AND (bound_flag != 1 OR connection_identifier == FF)`, returns 15 bytes: `01 20 01`, six stored peer bytes, six reversed local-address bytes | A one-byte success status is not a pairing-state read. Select the response contract by exact firmware and check complete length/fields |
| `59 0A` outside the data predicate | One-byte `01` | One-byte `01` without addresses | Treat missing address data as unavailable, never as verified association |

`P[2]` is ignored by the Prod selector branch; the data switch is `P[3]`. Its state predicate is evaluated before producing the address payload. Do not turn this payload-relative description into an assumed Prod outer-frame encoder.

The `58 0A 02` six-byte copy at `P[4..9]`, ignored `P[3]`, set rejection condition and seven-byte echo are shared by both reviewed handlers. They are recorded here as unchanged comparison context, not as an invented version delta. The application fix for the shifted byte is a client implementation correction, not a firmware API change.

The Test 1.02 frame relationship is documented in [the exact analyzed baseline](../reference/wocode.md#analyzed-baseline). The [reviewed EXT58/EXT59 contract](../appendices/k10-barrel-ext58.md) and [synthetic getter cases](../fixtures/k10-barrel-ext58.json) extend this evidence record. Deferred storage behavior is intentionally outside this API changelog until a corresponding BLE-visible effect is demonstrated.
