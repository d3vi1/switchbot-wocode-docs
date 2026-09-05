# BarrelPro Test 1.05 to Test 1.06: bounded WoCode API comparison

Date: 2026-09-05. Method: independent read-only Ghidra decompilation, raw-byte spot checks, and hashing of the two loaded firmware files. No function names, types, firmware, or device state were changed. No BLE commands were transmitted.

## Result for an API-facing changelog

The reviewed command branches do not establish any added or removed EXT selector between these two images. The concrete WoCode reply changes found are the reported firmware-version bytes and build-information bytes. The EXT command families, selected reply lengths, and mode predicates inspected here are unchanged.

This is a static API comparison, not an over-the-air capture. The complete app-facing GATT characteristic-to-dispatcher path was not proven in this pass. A public changelog must preserve that distinction and must not turn changed Ghidra names into claims that a command was added or removed.

## Exact inputs

| Version | Filename | Bytes | SHA-256 |
|---|---|---:|---|
| Test 1.05 | `WoSweeperMiniBarrelPro_app_test_V1005.bin` | 48,496 | `b7d8d880349cada3869988aa3b32d986f779896b0743d3022883a59d4114d3e4` |
| Test 1.06 | `WoSweeperMiniBarrelPro_app_test_V1006.bin` | 48,500 | `e5f5d03e707f9d816e1a5e9cbf53546cc91cb81eeb9beb006352a207750b3b6a` |

Loaded programs: `/SweeperMiniBarrelPro_Test_1.05` and `/SweeperMiniBarrelPro_Test_1.06`. The files under `S10/Mini/MCU` match the corresponding recovery application's firmware resources. File offset `0x238` maps to application address `0x0080E000`; matching the independently read code bytes corroborated this coordinate conversion for the inspected ranges.

## Code anchors, selected by behavior

| Role established by the body | Test 1.05 | Test 1.06 |
|---|---|---|
| Complete frame dispatcher: checks `57`, parses header mode/class | `0x00810F64` | `0x00810F68` |
| Basic class-0 payload dispatcher | `0x00810E84` | `0x00810E84` |
| EXT family dispatcher | `0x008109E8` | `0x008109E8` |
| EXT `22` branch handler | `0x00810D90` | `0x00810D90` |
| EXT `23` branch handler | `0x00810D14` | `0x00810D14` |
| Class-2 status-body builder | `0x00810F28` | `0x00810F2C` |

The Test 1.06 function at `0x00810F64` is a small return stub, not its complete frame dispatcher. Comparing identical addresses or the old `variant`/`invalidCommand` symbol labels would therefore misclassify the API change.

## Changed replies

Examples below identify complete mode-0 request bytes and dispatcher result bodies. They are derived from static code, not captured BLE notifications. Existing mode/state admission rules still apply.

| Request | Test 1.05 result | Test 1.06 result | Meaning established here |
|---|---|---|---|
| `57 00 03 00` | `01 01 05` | `01 01 06` | The version-report payload changes from `01 05` to `01 06`; the outer dispatcher supplies the leading success byte. |
| `57 00 03 01 00` | `01 00 07 E8 04 12 10 04 2B` | `01 00 07 E8 04 12 10 14 0C` | The build-information payload changes two time-field octets; this pass does not assign a timezone. |

The request branches and lengths remain the same: the class-0 payload handler returns 2 or 8 bytes respectively, and the complete dispatcher prepends its status byte. Other inspected class-0 selectors `05` and `06` retain the same local branch structure and lengths; the names of their called wrappers differ with the four-byte relocation and must not be interpreted as new token commands.

## Unchanged EXT branch surface

Let `P` begin at the EXT family byte. In both complete frame dispatchers, mode 0 uses `P = F + 2`; mode 1 uses `P = F + 6`.

| Family | Branches present in both images | Local reply behavior |
|---|---|---|
| `58` | Selectors `00`, `01`, `02`, `03`, `08`, `0A` | `00`: five bytes; `01/02/03`: four bytes; `08` suboperations `01/02`: four bytes; `0A`: behavior below. Other selector/suboperation paths can return the caller-initialized one-byte `01`. |
| `59` | Selectors `00`, `01`, `03`, `04`, `05`, `06`, `07`, `0A` | `00`: ten bytes; `01`: six bytes; `03` through `07` as listed: five bytes; `0A`: conditional fifteen-byte result, otherwise one byte. |
| `5A`, `5B` | No branch in this inspected EXT dispatcher | After header admission, the complete dispatcher returns its initialized one-byte `01`; that is not an implemented family-specific command or verified actuation. |
| `22` | Suboperations `01`, `02`, `03` | Same request-data guards and five/seven/nine-byte responses respectively. |
| `23` | Suboperations `01`, `02`, `03` | Same nineteen/seven/nine-byte responses respectively. |

For `58/00`, both versions clamp an input below 2 to 1 and an input above `90` to `91` when the same local state helper allows the operation. This is a shared baseline observation, not a 1.06 change.

### Shared Pro peer-command details

These details prevent accidentally applying the non-Pro contract to either Pro image; they are not changes between 1.05 and 1.06.

- `58/0A/01` clears the binding flag and six stored peer bytes and attempts to queue event 3 unconditionally within this branch. It returns one-byte `01`. This differs from the previously investigated non-Pro branch's conditional clear.
- `58/0A/02` rejects when the flag is 1 and the connection identifier is not `FF`; rejection is one-byte `02`.
- An accepted set copies `P[4..9]` into the stored peer and initially into the seven-byte response. It then overwrites **response byte 1 with `01`** before returning. For raw peer bytes `A0 A1 A2 A3 A4 A5`, the resulting body is `01 01 A1 A2 A3 A4 A5`, not an exact six-byte echo.
- The overwrite is visible in both independent decompilations and in identical raw bytes at `0x00810BEA`: `84 F8 01 80`, a store-byte to response offset 1. No hardware exchange was performed.
- Both getters `59/0A` require `P[3] == 01`, with `P[2]` unused in this selector. A fifteen-byte result is produced when the connection identifier is `FF`, or when the binding flag is not 1 and an additional referenced byte is zero. That additional byte's meaning is not assigned here.
- The getter's fifteen-byte body remains `01 20 01`, six stored peer bytes, and six reversed local-source bytes. A false predicate returns one-byte `01`.

### Shared `22` / `23` branches

The following describes local byte contracts only. Names such as pairing, token provisioning, or station renaming are not assigned to these opaque records without further evidence.

| EXT payload prefix | Required data / result in both versions |
|---|---|
| `22 01` | Requires at least 16 data bytes after the suboperation. Combines those with a stored 16-byte region for a helper call; returns `01` plus the four-byte helper result, most-significant byte first. Helper algorithm/semantic purpose remains unassigned. |
| `22 02` | Requires at least 6 data bytes. Copies them through storage-related calls and into a six-byte RAM field; returns `01` plus the six requested bytes. This is a state-changing branch, not a free diagnostic read. No live invocation was made. |
| `22 03` | Requires at least 8 data bytes. Passes/copies them into a different record region; returns `01` plus those eight bytes. Storage semantics remain bounded to the traced calls. |
| `22` unknown suboperation | Returns `01 05`. Insufficient data for a recognized suboperation returns one-byte `02`. |
| `23 01` | Returns `01`, a six-byte field, an eight-byte field, and a four-byte helper result: 19 bytes total. |
| `23 02` | Returns `01` plus the six-byte field: 7 bytes. |
| `23 03` | Returns `01` plus the eight-byte field: 9 bytes. |
| `23` unknown suboperation | Returns `01 05`. No local minimum-length guard was identified for reading its suboperation byte. |

The `22`/`23` computed-result helper moves from `0x00812E04` to `0x00812E08`. The sampled 12-byte helper range is identical; a cryptographic or token-algorithm name is not inferred from that equivalence.

## Header and authentication boundary

Both complete dispatchers show the same checks:

- Wrong magic is not processed and returns zero result length.
- Nonzero header bits 7–6 yield one-byte `04`.
- Class `0A` follows its dedicated mode-bypass path with payload offset 2; this exception must not be generalized to EXT class `0F`.
- For other classes, mode 0 is admitted when configuration byte `+0x10` bit 7 equals byte `+0x11` bit 5; otherwise the result is `07`.
- Mode 1 uses the same predicate: let `a` be bit 7 of byte `+0x10`, and `b` be the arithmetic sign extension of bit 5 of byte `+0x11` (0 or -1). Admission is `a == b` or a nonzero result from the four-byte comparison helper. Failed comparison yields `09`.
- Modes 2/3 yield `0A` in that gated path. The mode-1 token acquisition/meaning is not established by this comparison.

The comparison-helper code range sampled at `0x0080E472..0x0080E4CD` is byte-identical across the images. No changed local header or comparison predicate was found.

## Comparison evidence and limits

Direct raw-image comparison found only a changed call displacement inside the 784-byte EXT code range `0x008109E8..0x00810CF7`, and one changed call displacement in each `22`/`23` code range. Their fresh decompilations preserve the command predicates and reply construction. The outer dispatcher moves by four bytes and its relative branch displacements adjust accordingly; those offsets are not API additions.

The inspected complete frame dispatchers route the commands described above, but cross-reference enumeration did not resolve their incoming callers. The service/characteristic registration, event path, runtime security state, actual device actuation, and persistence remain unqualified. No complete command surface outside these selected handlers was claimed.

Suggested public changelog wording: **"Static comparison of BarrelPro Test 1.05 and 1.06: firmware-version and build-information reply values changed. No added or removed selector, reply-layout change, or mode-gate change was found in the reviewed EXT 22/23/58/59 paths; 5A/5B remain unimplemented fallthroughs in that dispatcher. App-facing GATT admission and hardware behavior remain unverified."**

Do not carry forward the old symbol-diff claim that Test 1.06 added a standard dispatcher and removed the Pro command API. The executable branches inspected here do not support that interpretation.

This report contains original semantic descriptions and factual byte layouts only. Raw firmware and decompiled vendor code were not copied into a public documentation repository. The MCP lease is released after this bounded comparison.
