# Re-Pair implementation plan

Approved on 2026-09-05. The publisher amendment names **Răzvan Corneliu VILT Persoană Fizică Autorizată** as the original application copyright holder. Store seller, tax and bank settings are configured separately from source copyright.

## Product decisions

Swift/SwiftUI on iOS 17+ and macOS 14+ comes first; Kotlin/Compose on Android 12+ follows. K10+ is the first release target while research covers Pro, S10 and attributed K11/K20 concurrently. Android target SDK requirements are checked at release.

Reads, diagnostics, identification, local aliases and qualified transient operations including suction tests are free. A repeatable native-store activation product grants a permanent entitlement for one robot–station MAC pair, with a base price of EUR 1.99 and the store's localized price displayed. Persistent configuration, re-pairing and qualified application OTA use that entitlement. Attempts and later persistent functions for the same pair are included; repair success is not guaranteed.

A robot with separate water and dust stations uses two pairs. Replacing either member creates a new pair. Apple activations work across iPhone, iPad and Mac; Google activations are separate. A community build may omit payment checks and retains capability checks by default.

Applications are GPLv3 with the agreed narrowly scoped store distribution permission for owned code. Original documentation, diagrams and fixtures are CC0. Vendor firmware, documentation and decompiled code are excluded from that dedication.

## Dependencies and ownership

| Stage | Work | Acceptance |
| --- | --- | --- |
| M0 | Recover history/local commits/GUI; inventory corpus; publisher and license boundaries; GitHub issues | Original work preserved, integration reviewed, concrete backlog |
| M1 | Shared WoCode framing and K10 contracts, then per-family deltas | Independently reviewed evidence, fixtures and capability catalog |
| M2 | Typed Swift identity/contracts/codecs, serialized BLE executor, simulator and purchase/restore prototype | Negative and firmware-derived conformance tests |
| M3 | Inkscape vector rigs, native UI, operation integration, StoreKit/CloudKit | Complete accessible workflows and durable pair activation |
| M4 | Coordinated K10 hardware qualification, independent review, distribution package | Exact tested combinations and concrete release artifact |
| M5 | Pro/S10 operations, attributed K11/K20 and directed application OTA transitions | Separate evidence and catalog entry for every new combination |
| M6 | Kotlin/BLE, Compose/vector geometry, Play Billing/private Drive | Shared fixture parity and Android-specific qualification |

The coordinator and at most three specialists work concurrently. Each owns named modules and an isolated worktree. Exactly one agent owns the Ghidra/MCP lease; independent reviewers take the lease only after it is released. Work follows issue → milestone → PR → verification → squash merge → close. Final review is independent of implementation.

## Application architecture and purchases

Use the [shared operation model](../reference/operations.md). QR/radio matching identifies inspected targets and never proves electrical compatibility. A station-only mutation selects a pair containing that station. No implicit write targets a third device.

Inkscape SVG sources have semantic groups for body, eyes, pupils, lids, brows, mouth and accessories. A deterministic exporter produces native geometry. Group transforms and compatible Bezier interpolation animate expressions. Decorative blinking is separate from telemetry; success expressions require verified outcomes. Include accessibility text, contrast and Reduced Motion.

StoreKit 2 and Play Billing validate purchase evidence. A private CloudKit or Google Drive appDataFolder ledger plus a protected local copy stores transaction evidence and pair assignments. There is no project-owned backend or account service. HMAC-SHA-256 uses a random secret kept in the private account storage and Keychain/Keystore locally. Transaction IDs are not secret keys, and store signatures do not automatically cover our MAC mapping.

Check private-cloud availability before a new purchase. Save a durable verified grant before finish/consume, make retries idempotent, deduplicate by transaction, and quarantine contradictory mappings. Restored grants work offline. Provide recovery export/import. Client-only refund detection and resistance to deliberate tampering have limits; do not advertise guarantees the architecture cannot enforce.

## Acceptance

Test lengths, offsets, byte order, modes, errors, fragmentation, timeout, wrong peripheral/QR, partial connectivity and interruption between writes. Verify both pairing endpoints after reconnect; demonstrate persistence separately. OTA requires exact image digest, source-to-target configuration, installed-version readback and tested recovery.

Purchase tests cover pending/cancel, duplicate transactions, cloud failure, reinstall, corrupt records and sync conflicts. Swift and Kotlin consume the same reviewed fixtures. Store builds expose no arbitrary-hex console. Vector tests cover geometry, scaling, accessibility and Reduced Motion.

Missing model hardware does not block offline research or implementation. It blocks declaring that model's operation hardware-tested and enabling it in release. Live device modifications and final publication use concrete targets/artifacts presented before the action.

The first linked deliverables are the [EXT58 contract](https://github.com/d3vi1/switchbot-wocode-docs/issues/2) and the [Swift pairing correction](https://github.com/d3vi1/Switchbot-K10-Re-Pair/issues/7).
