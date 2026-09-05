# Firmware corpus inventory

This directory contains original, public-ready inventory metadata and reproducible tooling. It contains no firmware binaries, decompilation, credentials, or private absolute source paths.

## Scope

The generator reads direct `.bin` entries under `Mini/MCU` and `.bin`, `.img`, or `.zip` entries in 21 explicitly selected role directories under `AWSMirror/version/wocaotech/firmwareV2`. It does not recurse into extracted root filesystems, Ghidra projects, analysis exports, or other mirror channels.

The relative paths preserve the original local mirror provenance. They do not assert a download URL, release authenticity, or a permission to redistribute the corresponding binary.

## Reproduce

Run the commands from the repository root. Requires Python 3.9 or later and an existing local corpus with the relative directory structure recorded in the inventory. The root can be anywhere on the machine.

```sh
python3 scripts/inventory_corpus.py --root "$CORPUS_ROOT" --output corpus/firmware-inventory.json
python3 scripts/validate_inventory.py corpus/firmware-inventory.json
```

To reproduce the same JSON bytes from unchanged inputs, pass the original inventory's `generated_at` value with `--generated-at`. Paths, role directories, entries, and digest groups are sorted deterministically. The default timestamp records the new run's start time.

Files are hashed using SHA-256 in 4 MiB chunks. Each read checks that its file size, modification time, and inode remain stable while hashing. A symlink is read only if it resolves inside the supplied root; its original alias path remains in the metadata. Input files are never changed.

The generator writes `inventory-checkpoint.json` after each batch. It is a partial work artifact marked `complete: false`, not the final inventory. If source reads fail, the final inventory remains marked incomplete and the command exits unsuccessfully. Exceptions are reduced to an error class/code so private paths cannot leak through exception messages.

## Interpret correctly

- `entries` records each selected source path, measured byte size, computed digest, qualified attribution hints, and anomaly flags.
- `content_aliases` groups identical file bytes by digest. Identical content is not evidence that two products are mechanically or electrically compatible.
- `directories` summarizes the selected paths in each source directory.
- `manifest_reconciliation` compares the existing 14-row MCU manifest with current hashes and sizes, and enumerates files that the old manifest omitted.
- `path_bytes` counts every file alias; `unique_content_bytes` counts each digest once. Neither is a count of distinct marketed releases.
- Marketed-model identities are explicitly unverified for each digest. In particular, opaque IDs `91AgWZ1n` and `sH5cQeLF`, and filenames containing `K20`, do not establish a marketed K20+ Pro identity.
- Role and package labels are hints. `ota`, `rmt`, `dfu`, `app`, `rtl`, `EVT`, and `PVT` do not by themselves establish CPU, transport, signing, production suitability, or update compatibility.

Known directory/filename mismatches are retained rather than silently corrected. This lets later identification evidence resolve them without rewriting provenance.

## Validation

The independent validator checks publication hygiene, relative paths, digest syntax, alias partitioning, digest/size agreement across aliases, deterministic source ordering, aggregate byte/count totals, and complete MCU-manifest reconciliation. It rejects an incomplete inventory and any per-digest identity promoted to verified without additional evidence.

The generator validates source stability during each read; the validator checks relationships within the produced artifact. Neither claims that a file's source is authentic or that any device operation is supported. A successful run is a corpus identity milestone, not protocol or hardware validation.
