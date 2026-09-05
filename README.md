# SwitchBot WoCode documentation

A practical, evidence-linked guide to understanding and repairing robot–station relationships.

This repository is being developed for K10+, K10+ Pro, S10 and additional model families as their identities and firmware are established. It does not yet declare a hardware-qualified repair procedure.

Original prose, diagrams and conformance data are dedicated under CC0 1.0. Firmware, vendor documentation and decompiled code are excluded. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md).

Swift application: [Switchbot-K10-Re-Pair](https://github.com/d3vi1/Switchbot-K10-Re-Pair).

## Start with your task

- [Identify the robot and station you have](guides/identify-your-devices.md).
- [Understand what is currently supported](models/README.md).
- [Read the K10 pairing investigation](guides/k10-pairing.md).
- [Understand firmware upgrades and downgrades](guides/application-firmware.md).
- [Follow the implementation roadmap](project/implementation-plan.md).

## Implement a client

Read [the evidence rules](reference/evidence.md), [the common framing boundary](reference/wocode.md), and [the operation model](reference/operations.md). The [capability catalog](catalog/capabilities.json) is machine-readable and deliberately contains no hardware-qualified operation yet. Empty qualification is a result, not permission to infer support.

Document schema version: **0.1.0**. Research descriptions may advance without enabling a release capability. An application pins a reviewed documentation commit and the catalog digest used for its build.

## Evidence and structural conformance

- [Read the K10 barrel EXT58/EXT59 contract](appendices/k10-barrel-ext58.md).
- [Inspect the machine-readable contract](contracts/k10-barrel-ext58.json) and [synthetic fixtures](fixtures/k10-barrel-ext58.json).
- [Review the firmware corpus identity checkpoint](corpus/m0-summary.md) and [reproduce the inventory](corpus/README.md).

Run `python3 scripts/validate_docs.py` to check local links, JSON, corpus identities and structural fixtures. These checks do not contact hardware or enable release operations.
