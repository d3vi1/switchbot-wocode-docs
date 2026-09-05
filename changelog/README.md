# BLE API change histories

These per-product histories describe changes a BLE client needs to understand. They are separate from the capability/version gates that decide whether the application may execute an operation.

Each comparison records exact image digests and channels, command or GATT endpoint, old and new request/reply behavior, acceptance conditions, client impact and evidence. Static handler differences are labeled static; a real BLE observation additionally needs a capture. Do not treat test and production version numbers as a proven chronological upgrade path.

Include added/removed commands, characteristic properties, request/response fields, status semantics, mode/token admission, routing and externally visible behavior. Exclude function renames, code coverage, implementation-only refactors, unrelated firmware features and internal storage details unless their BLE-visible effect is demonstrated.

## Products

- [SweeperMini](SweeperMini.md): K10+ robot.
- [SweeperMiniBarrel](SweeperMiniBarrel.md): K10+ barrel.
- [SweeperMiniPro](SweeperMiniPro.md): K10+ Pro robot.
- [SweeperMiniProBarrel](SweeperMiniProBarrel.md): K10+ Pro barrel; reconcile aliases SweeperMiniBarrelPro and SweeperMiniProBarrel by image hash.
- [SweeperOrigin](SweeperOrigin.md): S10 robot.
- [SweeperOriginWaterStation](SweeperOriginWaterStation.md): S10 Water Station; keep main and remote controller versions separate.
- [SweeperOriginDustStation](SweeperOriginDustStation.md): S10 dust/charging station; keep main and remote controller versions separate.

K11 and opaque/internal K20 image groups remain in the [model attribution ledger](../models/README.md) until the marketed product and component are established. They must not silently inherit another product's changelog.

## Entry format

For each reviewed comparison, record:

1. A stable entry ID and comparison date.
2. Both filenames, SHA-256 digests, channels and component roles. Say when release order is unknown.
3. GATT service/characteristic or command coordinates, including whether offsets are payload- or frame-relative.
4. Before/after request, reply and admission behavior, including unchanged fields needed to interpret the delta.
5. The impact on a BLE client and an explicit limitation if app-facing reachability remains unproved.
6. Evidence references, confidence kind (`static`, `capture`, `hardware`), and related conformance cases.

A newly discovered fact about one image is not automatically a version change. Absence of a branch must be traced before reporting a removed or added operation. Mechanical/electrical compatibility is outside an API changelog.
