# WoCode and WoCode-Ext framing boundary

The current K10 investigation begins with outer frames of the form `57 <header> <payload>`. Extended class `0F` carries families including `58`, `59`, `5A` and `5B`. These observations are not a universal framing promise for every SwitchBot product.

In Barrel Test 1.02, the analyzed outer dispatcher passes `frame + 2` to its extended handler in mode 0. Therefore a payload-relative offset of 4 means outer-frame offset 6. Documents always state the reference point for an offset.

Mode-0 acceptance depends on device state in the dispatcher. The recovered application's claim that pairing never needs encryption or a token is too broad. Mode 1 and token relationships remain a separate investigation; clients must not silently fall back to mode 0 after rejection.

## Analyzed baseline

The two preceding statements are static observations from `WoSweeperMiniBarrel_app_test_V1002.bin`, SHA-256 `0227cd90a7147c62985bc8a4080157e010b14e8a4ed69f7c2632535ae49479c5`, reviewed on 2026-09-05. The outer dispatcher at `0x00810CE4` selects the mode and supplies `frame + 2` in mode 0; the EXT handler at `0x00810950` copies payload offsets 4–9 for `58 0A 02`. The mode-0 gate compares configuration byte `+0x10` bit 7 with byte `+0x11` bit 5. These addresses identify this image only. This record does not establish the complete GATT admission path or qualify a real pairing operation.

## Transport layers

App-facing WoCode GATT, internal peer services, UART forwarding and controller HCI commands have different recipients and reply envelopes. An internal command template does not demonstrate that a phone can send the same bytes directly to a barrel and cause actuation.

The existing B000-family notes include client-discovery evidence that does not establish identical hosted services on both devices. Service roles and reachability need individual tracing. No app operation should be enabled solely because an internal function name suggests it exists.

## Response boundaries

Bare result payloads and framed notifications are separate layouts. A parser must select the documented envelope for the exact operation and profile, check its length and status, and correlate it with the selected peripheral. It must not guess offsets from whichever layout happens to fit.

BLE write acceptance, notification receipt and verified operation outcome are separate events. An unsolicited or late notification cannot satisfy another device's pending operation.
