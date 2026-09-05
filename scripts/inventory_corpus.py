#!/usr/bin/env python3
"""Inventory selected local firmware as original metadata; never alter inputs.

Only direct MCU .bin entries and the explicitly listed firmwareV2 role directories
are read. SHA-256 is streamed. No network, Ghidra, extraction, or device access.
Output paths are relative to --root; source binaries are never embedded.
"""

import argparse
import collections
import csv
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path


MIRROR = "AWSMirror/version/wocaotech/firmwareV2"
ROLES = (
    "WoSweeperMini_ble_rtl", "WoSweeperMiniBarrel_ble_rtl",
    "WoSweeperMiniPro_ble_rtl", "WoSweeperMiniProBarrel_ble",
    "WoSweeperMiniProBarrel_ble_rtl", "WoSweeperOrigin_ota_SU2",
    "WoSweeperOrigin_waterBase", "WoSweeperOrigin_waterBaseRemote",
    "WoSweeperOrigin_chargeBase", "WoSweeperOrigin_chargeBaseRemote",
    "91AgWZ1n_ota", "91AgWZ1n_ota_SY4", "91AgWZ1n_chargeBase",
    "91AgWZ1n_chargeBaseRemote", "91AgWZ1n_handleVacuum",
    "91AgWZ1n_handleVacuumRemote", "sH5cQeLF_ota", "sH5cQeLF_ota_SY4",
    "sH5cQeLF_ota_SY5", "sH5cQeLF_chargeBase", "sH5cQeLF_chargeBaseRemote",
)
EXTENSIONS = {".bin", ".img", ".zip"}


def stream_digest(path):
    """Fail if size/mtime/inode changes during a bounded-memory read."""
    before = path.stat()
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    after = path.stat()
    if ((before.st_size, before.st_mtime_ns, before.st_ino) !=
            (after.st_size, after.st_mtime_ns, after.st_ino) or size != after.st_size):
        raise RuntimeError("input_changed_during_read")
    return digest.hexdigest(), size


def filename_hint(name):
    low = name.lower()
    if "handheld" in low or "handlevacuum" in low:
        return "k20-named", "handheld-vacuum"
    if "k20" in low:
        return "k20-named", "charging-station" if "_db_" in low else "unresolved"
    if "s10" in low:
        role = "water-station" if "_wb_" in low else (
            "charging-station" if any(x in low for x in ("dustbase", "_db_", "jichen")) else "unresolved")
        return "sweeper-origin", role
    if "miniprobarrel" in low or "minibarrelpro" in low or "k10plusprobarrel" in low:
        return "sweeper-mini-pro", "barrel"
    if "minipro" in low or "k10pluspro" in low:
        return "sweeper-mini-pro", "robot"
    if "minibarrel" in low:
        return "sweeper-mini", "barrel"
    if "sweepermini" in low:
        return "sweeper-mini", "robot"
    if "hub2" in low:
        return "hub2", "hub"
    return "unresolved", "unresolved"


def directory_hint(name):
    if name == "MCU":
        return "mixed-mcu-collection", "unresolved"
    if name.startswith("91AgWZ1n_") or name.startswith("sH5cQeLF_"):
        family = name.split("_", 1)[0]
    elif name.startswith("WoSweeperOrigin_"):
        family = "sweeper-origin"
    elif "Pro" in name:
        family = "sweeper-mini-pro"
    else:
        family = "sweeper-mini"
    if "waterBase" in name:
        role = "water-station"
    elif "chargeBase" in name:
        role = "charging-station"
    elif "handleVacuum" in name:
        role = "handheld-vacuum"
    elif "Barrel" in name:
        role = "barrel"
    else:
        role = "robot"
    return family, role


def attribution(path):
    directory_family, directory_role = directory_hint(path.parent.name)
    named_family, named_role = filename_hint(path.name)
    family = named_family if directory_family == "mixed-mcu-collection" else directory_family
    candidate = {"sweeper-mini": "K10+", "sweeper-mini-pro": "K10+ Pro",
                 "sweeper-origin": "S10"}.get(family)
    result = {
        "directory_internal_family_hint": directory_family,
        "directory_component_role_hint": directory_role,
        "filename_family_hint": named_family,
        "filename_component_role_hint": named_role,
        "marketed_model": {"status": "unverified_for_this_digest",
                           "candidate": candidate,
                           "basis": "filename_and_directory_metadata_only"},
        "hardware_revision": "unknown",
        "firmware_compatibility": "not_established",
    }
    if family in {"91AgWZ1n", "sH5cQeLF"} or named_family == "k20-named":
        result["marketed_model"] = {
            "status": "unresolved",
            "candidate": None,
            "basis": "opaque_directory_id_and_K20_named_files_do_not_establish_marketed_model",
        }
    low = path.name.lower()
    result["package_label_hints"] = sorted(set(re.findall(
        r"(?:^|_)(ota|oat|rmt|dfu|app|full|rtl|evt|pvt|dvt\d*|prod|test)(?=_|\.|$)", low)))
    result["version_label_hint"] = next(iter(re.findall(r"(?:^|_)([vV]\d+)(?=_|\.|$)", path.name)), None)
    result["component_implementation"] = "unverified; role and package labels are not CPU or transport evidence"
    flags = []
    if path.name.strip() != path.name or re.search(r"\s+\.bin$", path.name):
        flags.append("filename_contains_edge_whitespace")
    if directory_family != "mixed-mcu-collection":
        if named_role != "unresolved" and named_role != directory_role:
            flags.append("directory_filename_role_mismatch")
        if named_family not in {"unresolved", "k20-named"} and named_family != directory_family:
            flags.append("directory_filename_family_mismatch")
        if named_family == "k20-named" and directory_family not in {"91AgWZ1n", "sH5cQeLF"}:
            flags.append("directory_filename_family_mismatch")
    elif named_family == "hub2":
        flags.append("non_vacuum_image_in_mcu_collection")
    return result, flags


def write_json(path, obj):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Local corpus root; never serialized")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", help="Fixed ISO timestamp for byte-reproducible output")
    parser.add_argument("--checkpoint-every", type=int, default=20)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    timestamp = args.generated_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    selected, missing_directories = [], []
    scopes = ["Mini/MCU"] + [f"{MIRROR}/{name}" for name in ROLES]
    for relative in scopes:
        folder = root / relative
        if not folder.is_dir():
            missing_directories.append(relative)
            continue
        extensions = {".bin"} if relative == "Mini/MCU" else EXTENSIONS
        selected.extend(path for path in folder.iterdir()
                        if path.is_file() and path.suffix.lower() in extensions)
    selected.sort(key=lambda path: path.relative_to(root).as_posix())
    manifest_path = root / "Mini/MCU/manifest.tsv"
    manifest_hash, manifest_size = stream_digest(manifest_path)
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    entries, failures = [], []
    estimated_bytes = sum(path.stat().st_size for path in selected)
    print(json.dumps({"event": "started", "files": len(selected), "bytes": estimated_bytes}), flush=True)
    for index, path in enumerate(selected, 1):
        relative = path.relative_to(root).as_posix()
        try:
            # Do not follow a corpus alias outside the explicitly supplied root.
            if not path.resolve().is_relative_to(root):
                raise RuntimeError("symlink_target_outside_root")
            digest, size = stream_digest(path)
            hints, flags = attribution(path)
            entries.append({"source_path": relative, "size_bytes": size, "sha256": digest,
                            "is_symlink": path.is_symlink(), "attribution": hints,
                            "anomaly_flags": flags})
        except (OSError, RuntimeError) as error:
            # Never serialize exception text; it can contain private absolute paths.
            failures.append({"source_path": relative, "error_kind": type(error).__name__,
                             "error_code": getattr(error, "errno", None)})
        if index % args.checkpoint_every == 0 or index == len(selected):
            checkpoint = {"schema_version": 1, "complete": False,
                          "generated_at": timestamp, "selected_file_count": len(selected),
                          "processed_file_count": index, "entries": entries, "failures": failures}
            write_json(output.with_name("inventory-checkpoint.json"), checkpoint)
            print(json.dumps({"event": "progress", "processed": index, "total": len(selected),
                              "hashed_bytes": sum(x["size_bytes"] for x in entries),
                              "failures": len(failures)}), flush=True)
    by_path = {entry["source_path"]: entry for entry in entries}
    manifest_results = []
    listed_paths = set()
    for row in manifest:
        relative = "Mini/MCU/" + row["file"]
        listed_paths.add(relative)
        actual = by_path.get(relative)
        manifest_results.append({"source_path": relative, "expected_sha256": row["sha256"],
                                 "expected_size_bytes": int(row["size_bytes"]),
                                 "digest_matches": bool(actual and actual["sha256"] == row["sha256"]),
                                 "size_matches": bool(actual and actual["size_bytes"] == int(row["size_bytes"])),
                                 "selected_and_hashed": actual is not None})
    unlisted = sorted(path for path in by_path if path.startswith("Mini/MCU/") and path not in listed_paths)
    grouped = collections.defaultdict(list)
    for entry in entries:
        grouped[entry["sha256"]].append(entry)
    aliases = [{"sha256": digest, "size_bytes": values[0]["size_bytes"],
                "source_paths": sorted(value["source_path"] for value in values)}
               for digest, values in sorted(grouped.items())]
    directories = []
    for relative in scopes:
        matching = [entry for entry in entries if str(Path(entry["source_path"]).parent) == relative]
        directories.append({"source_directory": relative, "file_count": len(matching),
                            "bytes": sum(x["size_bytes"] for x in matching),
                            "unique_sha256_count": len({x["sha256"] for x in matching})})
    result = {
        "schema_version": 1, "complete": not failures and not missing_directories,
        "generated_at": timestamp, "hash_algorithm": "SHA-256",
        "scope": {"source_directories": scopes, "recursive": False,
                  "mcu_extensions": [".bin"], "mirror_extensions": sorted(EXTENSIONS),
                  "excluded": ["extracted filesystems", "Ghidra projects", "analysis artifacts", "other mirror channels"]},
        "interpretation": {
            "hash_equivalence": "Equal digests identify identical file bytes, not hardware compatibility or distinct releases.",
            "model_attribution": "All per-digest marketed identities remain unverified in this metadata-only inventory.",
            "source_provenance": "Paths are original relative locations beneath a caller-supplied local corpus root.",
            "publication": "Original inventory metadata only; no firmware bytes, decompilation, credentials, or absolute local paths.",
        },
        "counts": {"selected_files": len(selected), "hashed_files": len(entries),
                   "path_bytes": sum(x["size_bytes"] for x in entries),
                   "unique_sha256": len(aliases), "unique_content_bytes": sum(x["size_bytes"] for x in aliases),
                   "duplicate_content_groups": sum(len(x["source_paths"]) > 1 for x in aliases),
                   "anomalous_paths": sum(bool(x["anomaly_flags"]) for x in entries)},
        "manifest_reconciliation": {"source_path": "Mini/MCU/manifest.tsv",
                                    "source_sha256": manifest_hash, "source_size_bytes": manifest_size,
                                    "listed_entries": len(manifest), "entries": manifest_results,
                                    "unlisted_hashed_entries": len(unlisted), "unlisted_source_paths": unlisted},
        "directories": directories, "entries": entries, "content_aliases": aliases,
        "failures": failures, "missing_source_directories": missing_directories,
    }
    write_json(output, result)
    print(json.dumps({"event": "complete", "complete": result["complete"], **result["counts"]}), flush=True)
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
