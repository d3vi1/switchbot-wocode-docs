# M0 corpus identity checkpoint

The selected corpus has been fully streamed through SHA-256 twice. This checkpoint identifies file content and its relative provenance; it does not establish per-device compatibility or marketed-model identity.

| Measure | Result |
|---|---|
| Source paths | 432 |
| Bytes across all paths | 12,050,701,063 |
| Unique content digests | 277 |
| Bytes counting each digest once | 10,840,830,597 |
| Digests with multiple aliases | 103 |
| Paths with attribution anomalies | 3 |
| Read failures or missing scope directories | 0 |

## MCU manifest reconciliation

The existing manifest lists 14 entries. Every listed SHA-256 and byte size matches the corresponding file. Another 52 MCU bins are present and now inventoried, yielding 66 MCU paths. The manifest is therefore a valid partial registry, not a complete inventory of the current MCU directory.

## Qualified anomalies

- `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMini_ble_rtl/WoSweeperMiniBarrel_rtl_app_V1001.bin`: directory_filename_role_mismatch.
- `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_chargeBaseRemote/K20_HandheldVacuum_app_v20_240611.bin`: directory_filename_role_mismatch, directory_filename_family_mismatch.
- `Mini/MCU/Hub2_aws_iot_no_boot_V111.bin`: non_vacuum_image_in_mcu_collection.

These are metadata conflicts or scope outliers, not proof that the corresponding binary is defective. They remain in the inventory without renaming or moving source files.

## Selected directories

| Relative source directory | Paths | Unique digests in directory | Bytes |
|---|---:|---:|---:|
| `Mini/MCU` | 66 | 51 | 5,091,640 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMini_ble_rtl` | 6 | 4 | 213,352 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMiniBarrel_ble_rtl` | 4 | 3 | 194,892 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMiniPro_ble_rtl` | 3 | 2 | 105,796 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMiniProBarrel_ble` | 1 | 1 | 48,788 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperMiniProBarrel_ble_rtl` | 2 | 2 | 97,776 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_ota_SU2` | 123 | 123 | 8,754,054,592 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_waterBase` | 10 | 10 | 789,968 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_waterBaseRemote` | 9 | 9 | 702,236 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_chargeBase` | 6 | 6 | 435,152 |
| `AWSMirror/version/wocaotech/firmwareV2/WoSweeperOrigin_chargeBaseRemote` | 7 | 7 | 557,076 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_ota` | 1 | 1 | 52,383,408 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_ota_SY4` | 38 | 38 | 1,630,508,362 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_chargeBase` | 32 | 19 | 1,955,732 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_chargeBaseRemote` | 30 | 17 | 1,728,148 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_handleVacuum` | 17 | 9 | 2,189,468 |
| `AWSMirror/version/wocaotech/firmwareV2/91AgWZ1n_handleVacuumRemote` | 15 | 9 | 1,970,788 |
| `AWSMirror/version/wocaotech/firmwareV2/sH5cQeLF_ota` | 1 | 1 | 52,383,408 |
| `AWSMirror/version/wocaotech/firmwareV2/sH5cQeLF_ota_SY4` | 2 | 2 | 84,494,573 |
| `AWSMirror/version/wocaotech/firmwareV2/sH5cQeLF_ota_SY5` | 34 | 34 | 1,459,299,896 |
| `AWSMirror/version/wocaotech/firmwareV2/sH5cQeLF_chargeBase` | 12 | 11 | 737,932 |
| `AWSMirror/version/wocaotech/firmwareV2/sH5cQeLF_chargeBaseRemote` | 13 | 12 | 758,080 |

## Interpretation and validation

- Filenames and directory labels supply component and family hints only; all digest-level marketed-model identities remain unresolved or unverified.
- In particular, `91AgWZ1n`, `sH5cQeLF`, and `K20` filenames are not mapped to marketed K20+ Pro.
- Equal hashes establish identical bytes, not compatibility, release-channel authenticity, or a supported firmware transition.
- The validator passed relative-path/privacy checks, alias partition checks, all count/byte reconciliations, and all 14 manifest SHA/size checks.
- A second complete hash pass reproduced all content and metadata; normalization to the same caller-supplied timestamp reproduced the first artifact bytes exactly.
- No source firmware, repository, Ghidra state, device, or extracted root filesystem was modified.

Artifacts: [inventory](firmware-inventory.json), [generator](../scripts/inventory_corpus.py), [validator](../scripts/validate_inventory.py), [validation evidence](validation.json), [reproduction instructions](README.md).
