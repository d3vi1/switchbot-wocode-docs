# WoCode and WoCode-Ext framing boundary

The current K10 investigation begins with outer frames of the form `57 <header> <payload>`. Extended class `0F` carries families including `58`, `59`, `5A` and `5B`. These observations are not a universal framing promise for every SwitchBot product.

In Barrel Test 1.02, the analyzed outer dispatcher passes `frame + 2` to its extended handler in mode 0. Therefore a payload-relative offset of 4 means outer-frame offset 6. Documents always state the reference point for an offset.

Mode-0 acceptance depends on device state in the dispatcher. The recovered application's claim that pairing never needs encryption or a token is too broad. The Prod 1.04 mode-1 byte comparison is now traced, but the check value's provisioning and meaning remain unresolved. Clients must not silently fall back to mode 0 after rejection.

## Analyzed baseline

The Test 1.02 outer-frame relationship and mode-0 gate above are static observations from `WoSweeperMiniBarrel_app_test_V1002.bin`, SHA-256 `0227cd90a7147c62985bc8a4080157e010b14e8a4ed69f7c2632535ae49479c5`, reviewed on 2026-09-05. The outer dispatcher at `0x00810CE4` selects the mode and supplies `frame + 2` in mode 0; the EXT handler at `0x00810950` copies payload offsets 4–9 for `58 0A 02`. The mode-0 gate compares configuration byte `+0x10` bit 7 with byte `+0x11` bit 5. These addresses identify this image only. This record does not establish the complete GATT admission path or qualify a real pairing operation.

## Production 1.04 normal GATT

For `WoSweeperMiniBarrel_app_prod_V1004.bin`, SHA-256 `997788eedfa24ddf4b7d7c082b9b8994578296c437c3b11802224f957c5cb219`, the actual outer dispatcher is `0x00810D28`. Worker call `0x00816C0E` supplies the staged full frame; the EXT tail branch at `0x00810E34` passes F + 2 in mode 0 or F + 6 in mode 1 to `0x00810950`.

The normal `CBA20D00` service registration, `CBA20002` write path and `CBA20003` response submission are statically connected. The response body is submitted without another WoCode prefix. This profile applies only when bootstrap helper `0x00812934` does not return 2. Busy staging, absent local length checks, mode predicates, exact UUIDs and response initialization are documented in the [production ingress reference](../appendices/k10-barrel-prod104-ingress.md). Runtime delivery and hardware qualification remain open, and this evidence does not expand the Test 1.02 scope above.

## Transport layers

App-facing WoCode GATT, internal peer services, UART forwarding and controller HCI commands have different recipients and reply envelopes. An internal command template does not demonstrate that a phone can send the same bytes directly to a barrel and cause actuation.

The existing B000-family notes include client-discovery evidence that does not establish identical hosted services on both devices. Service roles and reachability need individual tracing. No app operation should be enabled solely because an internal function name suggests it exists.

## Response boundaries

Bare result payloads and framed notifications are separate layouts. A parser must select the documented envelope for the exact operation and profile, check its length and status, and correlate it with the selected peripheral. It must not guess offsets from whichever layout happens to fit.

BLE write acceptance, notification receipt and verified operation outcome are separate events. An unsolicited or late notification cannot satisfy another device's pending operation.
