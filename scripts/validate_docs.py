#!/usr/bin/env python3
"""Validate original docs, evidence identities and synthetic structural fixtures.

These checks never contact a device, fetch a URL, or claim hardware validation.
Run from any directory; --root defaults to this script's repository parent.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def check_repository(root):
    errors = []
    counts = {"markdown_links": 0, "json_documents": 0, "structural_cases": 0}

    def require(condition, message):
        if not condition:
            errors.append(message)

    def relative(path):
        return path.relative_to(root).as_posix()

    def load(path):
        try:
            return json.loads((root / path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            errors.append(f"{path}: {type(error).__name__}")
            return None

    json_files = [p for p in root.rglob("*.json") if ".git" not in p.parts]
    for path in json_files:
        try:
            json_text = path.read_text(encoding="utf-8")
            json.loads(json_text)
            require("/Users/" not in json_text and "file://" not in json_text,
                    f"{relative(path)}: private absolute path")
            counts["json_documents"] += 1
        except ValueError:
            errors.append(f"{relative(path)}: invalid JSON")
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        require(not re.search(r"^(?:<{7}|={7}|>{7})(?: |$)", text, flags=re.M),
                f"{relative(path)}: unresolved merge conflict marker")
        require("/Users/" not in text and "file://" not in text, f"{relative(path)}: private absolute path")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            counts["markdown_links"] += 1
            require(destination.is_relative_to(root), f"{relative(path)}: link leaves repository")
            require(destination.exists(), f"{relative(path)}: missing link {target}")
            if parsed.fragment and destination.is_file() and destination.suffix == ".md":
                headings = re.findall(r"^#{1,6}\s+(.+)$", destination.read_text(), flags=re.M)
                slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
                require(unquote(parsed.fragment) in slugs, f"{relative(path)}: missing heading {target}")

    corpus = load("corpus/firmware-inventory.json")
    validation = load("corpus/validation.json")
    contract = load("contracts/k10-barrel-ext58.json")
    fixtures = load("fixtures/k10-barrel-ext58.json")
    if not all(x is not None for x in (corpus, validation, contract, fixtures)):
        return errors, counts
    inventory_bytes = (root / "corpus/firmware-inventory.json").read_bytes()
    require(hashlib.sha256(inventory_bytes).hexdigest() == validation["inventory_sha256"], "inventory validation digest is stale")
    for key, name in [("generator_sha256", "inventory_corpus.py"), ("validator_sha256", "validate_inventory.py")]:
        require(hashlib.sha256((root / "scripts" / name).read_bytes()).hexdigest() == validation[key], f"{name}: validation digest is stale")
    run = subprocess.run([sys.executable, str(root / "scripts/validate_inventory.py"),
                          str(root / "corpus/firmware-inventory.json")], capture_output=True, text=True)
    require(run.returncode == 0, "independent inventory validation failed")
    require(contract["hardware_qualified"] is False and contract["release_enabled"] is False,
            "static contract must not enable a release capability")
    require(fixtures["hardware_qualified"] is False, "synthetic fixtures are not hardware qualified")
    require(fixtures["contract_id"] == contract["contract_id"], "fixture contract id mismatch")
    profiles = {x["id"]: x for x in contract["profiles"]}
    by_digest = {x["sha256"]: x for x in corpus["content_aliases"]}
    for profile in profiles.values():
        digest = profile["firmware_sha256"]
        require(digest in by_digest, "contract firmware digest absent from inventory")
        if digest in by_digest:
            require(any(Path(p).name == profile["firmware_filename"] for p in by_digest[digest]["source_paths"]),
                    "contract filename is not an alias of its digest")
        require(profile["hardware_qualified"] is False, "profile is not hardware qualified")
    for key, path in contract["references"].items():
        require((root / "contracts" / path).resolve().is_file(), f"missing contract reference {key}")
    require(profiles["barrel-prod-1.04"]["mode0_full_frame_coordinates_verified"] is False,
            "production full frame mapping remains unresolved")
    setter = contract["set_peer"]
    require(setter["test_mode0_peer_offset"] == contract["coordinates"]["test_1_02_mode0_payload_offset"] + setter["payload_peer_offset"],
            "setter payload/full frame coordinates disagree")
    require(setter["test_mode0_peer_offset"] + setter["peer_length"] == setter["host_exact_frame_length"],
            "setter host frame does not supply the full peer field")
    require(setter["accepted_reply_peer_offset"] + setter["peer_length"] == setter["accepted_reply_length"],
            "setter reply field geometry disagrees")
    seen = set()
    for case in fixtures["cases"]:
        counts["structural_cases"] += 1
        case_id = case["id"]
        require(case_id not in seen, "duplicate fixture id " + case_id)
        seen.add(case_id)
        require(case["profile_id"] in profiles, "unknown fixture profile " + case_id)
        kind = case["kind"]
        state = case.get("initial_state", {})
        flag = state.get("binding_flag")
        connection = int(state["connection_identifier_hex"], 16) if "connection_identifier_hex" in state else None
        request = bytes.fromhex(case.get("request_hex", ""))
        def same(actual, expected_hex, label):
            require(actual == bytes.fromhex(expected_hex), f"{case_id}: {label} disagrees")
        if kind == "handler_set":
            require(len(request) == setter["host_exact_frame_length"], f"{case_id}: setter frame length")
            same(request[:5], setter["test_mode0_frame_prefix_hex"], "setter prefix")
            rejected = flag == 1 and connection != 255
            peer = request[setter["test_mode0_peer_offset"]:setter["test_mode0_peer_offset"] + setter["peer_length"]]
            reply = b"\x02" if rejected else b"\x01" + peer
            same(reply, case["expected_reply_hex"], "state-gated setter reply")
            require(case["expected_mutation"] is (not rejected), f"{case_id}: mutation predicate")
            if not rejected:
                same(peer, case["expected_peer_hex"], "peer byte offset")
        elif kind == "host_request_validation":
            require(case["host_accepts"] is (len(request) == setter["host_exact_frame_length"]), f"{case_id}: host length guard")
            staging = request + bytes(247 - len(request))
            same(staging[6:12], case["conditional_zero_staging_peer_hex"], "conditional short-frame shift")
        elif kind == "handler_clear":
            same(request, contract["clear_peer"]["test_mode0_frame_hex"], "clear frame")
            change = flag != 0 or connection == 255
            require(case["expected_mutation"] is change and case["expected_event3"] is change, f"{case_id}: clear predicate")
            same(b"\x01", case["expected_reply_hex"], "clear response")
        elif kind == "unsupported_operation":
            same(request[:4], "57 0F 58 0A", "unsupported selector prefix")
            require(request[4] not in (1, 2) and case["expected_mutation"] is False, f"{case_id}: unsupported operation")
            same(b"\x01", case["expected_reply_hex"], "unsupported response")
        elif kind == "getter_stub":
            same(request[:4], "57 0F 59 0A", "getter selector prefix")
            require(case["profile_id"] == "barrel-test-1.02" and case["contains_peer_data"] is False, f"{case_id}: test getter")
            same(b"\x01", case["expected_reply_hex"], "stub response")
        elif kind == "production_getter":
            payload = bytes.fromhex(case["request_payload_hex"])
            same(payload[:2], "59 0A", "production getter selector prefix")
            getter = contract["get_peer"]["prod_1_04"]
            require(case["profile_id"] == "barrel-prod-1.04" and len(payload) >= 4, f"{case_id}: production payload")
            has_data = payload[getter["query_byte_offset"]] == 1 and (flag != 1 or connection == 255)
            reply = b"\x01\x20\x01" + bytes.fromhex(state["stored_peer_hex"]) + bytes.fromhex(state["local_source_2_to_7_hex"])[::-1] if has_data else b"\x01"
            same(reply, case["expected_reply_hex"], "production getter layout/predicate")
            require(case["contains_peer_data"] is has_data, f"{case_id}: production getter data availability")
        elif kind == "header_gate":
            accepted = case["config_10_bit7"] == case["config_11_bit5"]
            require(case["accepts"] is accepted, f"{case_id}: mode0 gate")
            require(case["rejection_reply_hex"] == (None if accepted else "07"), f"{case_id}: mode0 rejection")
        elif kind == "client_reply_validation":
            reply = bytes.fromhex(case["reply_hex"])
            peer = bytes.fromhex(case["intended_peer_hex"])
            valid = len(reply) == 7 and reply == b"\x01" + peer
            require(case["echo_verified"] is valid and case["hardware_pairing_verified"] is False,
                    f"{case_id}: exact echo/hardware boundary")
        else:
            errors.append(f"{case_id}: unknown fixture kind {kind}")
    return errors, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        errors, counts = check_repository(args.root.resolve())
    except (KeyError, TypeError, ValueError, OSError) as error:
        errors, counts = ["Malformed contract or fixture: " + type(error).__name__], {}
    print(json.dumps({"valid": not errors, "checks": counts, "errors": errors,
                      "hardware_validation_performed": False}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
