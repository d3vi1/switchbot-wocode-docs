#!/usr/bin/env python3
"""Independently check publication hygiene and inventory relationships."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    raw = args.inventory.read_bytes()
    data = json.loads(raw)
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def visit(value, key=""):
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif isinstance(value, str):
            check(not value.startswith(("/", "file://", "~", "C:\\")), "absolute-path-like string")
            check("/Users/" not in value and "/home/" not in value, "private home-directory marker")
            if key in {"source_path", "source_paths", "source_directory", "source_directories",
                       "unlisted_source_paths", "missing_source_directories"}:
                check(".." not in PurePosixPath(value).parts, "relative path traversal")
            if key.endswith("sha256"):
                check(re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid digest syntax")

    visit(data)
    check(data.get("complete") is True, "inventory is incomplete")
    check(not data.get("failures"), "hash failures present")
    check(not data.get("missing_source_directories"), "source directories missing")
    entries = data["entries"]
    by_path = {entry["source_path"]: entry for entry in entries}
    check(len(by_path) == len(entries), "duplicate source paths")
    check(list(by_path) == sorted(by_path), "source paths not deterministically sorted")
    check(all(entry["size_bytes"] >= 0 for entry in entries), "negative size")
    check(all(entry["attribution"]["marketed_model"]["status"] in
              {"unverified_for_this_digest", "unresolved"} for entry in entries),
          "metadata promoted to verified model identity")
    alias_paths = []
    for group in data["content_aliases"]:
        for path in group["source_paths"]:
            check(path in by_path, "alias path absent from entries")
            if path in by_path:
                check(by_path[path]["sha256"] == group["sha256"], "alias digest mismatch")
                check(by_path[path]["size_bytes"] == group["size_bytes"], "alias size mismatch")
            alias_paths.append(path)
    check(sorted(alias_paths) == sorted(by_path), "aliases do not partition file entries")
    counts = data["counts"]
    check(counts["selected_files"] == counts["hashed_files"] == len(entries), "file count mismatch")
    check(counts["path_bytes"] == sum(x["size_bytes"] for x in entries), "path byte count mismatch")
    check(counts["unique_sha256"] == len({x["sha256"] for x in entries}) == len(data["content_aliases"]),
          "unique digest count mismatch")
    check(counts["unique_content_bytes"] == sum(x["size_bytes"] for x in data["content_aliases"]),
          "unique byte count mismatch")
    manifest = data["manifest_reconciliation"]
    check(manifest["listed_entries"] == len(manifest["entries"]), "manifest row count mismatch")
    check(all(x["selected_and_hashed"] and x["digest_matches"] and x["size_matches"]
              for x in manifest["entries"]), "manifest digest, size, or selection mismatch")
    unlisted = manifest["unlisted_source_paths"]
    listed = {x["source_path"] for x in manifest["entries"]}
    mcu = {path for path in by_path if path.startswith("Mini/MCU/")}
    check(set(unlisted) == mcu - listed, "unlisted MCU reconciliation mismatch")
    check(manifest["unlisted_hashed_entries"] == len(unlisted), "unlisted count mismatch")
    check(sum(x["file_count"] for x in data["directories"]) == len(entries), "directory counts mismatch")
    check(sum(x["bytes"] for x in data["directories"]) == counts["path_bytes"], "directory bytes mismatch")
    print(json.dumps({"valid": not errors, "inventory_sha256": hashlib.sha256(raw).hexdigest(),
                      "file_count": len(entries), "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
