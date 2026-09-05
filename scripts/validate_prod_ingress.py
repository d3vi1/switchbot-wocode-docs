"""Check original Prod 1.04 semantic contracts and synthetic examples offline."""


def header_result(frame, a, b, check):
    """Independent expression of the reviewed EXT header branches; not firmware code."""
    if len(frame) < 2:
        raise ValueError("fixture must supply both header bytes; firmware has no local guard")
    if frame[0] != 0x57:
        return None, b""
    if frame[1] & 0xC0:
        return None, b"\x04"
    if frame[1] & 0x0F != 0x0F:
        raise ValueError("fixture is outside the reviewed EXT class")
    if a not in (0, 1) or b not in (0, 1) or len(check) != 4:
        raise ValueError("invalid synthetic configuration")
    mode = (frame[1] >> 4) & 3
    if mode == 0:
        return (2, None) if a == b else (None, b"\x07")
    if mode == 1:
        if len(frame) < 6:
            raise ValueError("mode-1 fixture does not supply comparison bytes")
        return (6, None) if a + b == 0 or frame[2:6] == check else (None, b"\x09")
    return None, b"\x0a"


def check_prod_ingress(contract, fixtures, main, catalog, require, counts):
    profile = next(p for p in main["profiles"] if p["id"] == "barrel-prod-1.04")
    require(contract["profile_id"] == fixtures["profile_id"] == profile["id"], "production ingress profile mismatch")
    require(contract["firmware_sha256"] == fixtures["firmware_sha256"] == profile["firmware_sha256"],
            "production ingress firmware digest mismatch")
    require(contract["firmware_filename"] == profile["firmware_filename"], "production ingress filename mismatch")
    require(contract["contract_id"] == fixtures["contract_id"], "production ingress fixture contract mismatch")
    require(contract["qualification"] == "static_analysis_only" and contract["hardware_qualified"] is False
            and contract["release_enabled"] is False and fixtures["hardware_qualified"] is False,
            "production static evidence must not become hardware qualification")
    require(catalog["profiles"] == [] and catalog["firmwareTransitions"] == [], "static ingress must not enable catalog capabilities")
    points = contract["entrypoints"]
    for key, expected in {"registration": "0x00812694", "service_wrapper": "0x00816314",
                          "write_callback": "0x008163B4", "application_callback": "0x00811EAC",
                          "worker_dispatch_call": "0x00816C0E", "full_frame_dispatcher": "0x00810D28",
                          "reply_initialization": "0x00810D8A", "ext_tail_branch": "0x00810E34",
                          "ext_handler": "0x00810950", "reply_submission_call": "0x00816C2A",
                          "reply_wrapper": "0x00816464", "reply_send_rom": "0x0004F7A4"}.items():
        require(int(points[key], 16) == int(expected, 16), "pinned production entrypoint mismatch: " + key)
    require(int(points["registered_thumb_callback"], 16) == int(points["application_callback"], 16) + 1,
            "registered callback Thumb pointer disagrees with body")
    require(profile["full_frame_dispatcher_address"] == points["full_frame_dispatcher"]
            and profile["ext_parser_address"] == points["ext_handler"], "main/ingress dispatcher anchors disagree")
    require(profile["mode0_full_frame_coordinates_verified"] is True
            and profile["mode1_full_frame_coordinates_verified"] is True,
            "production coordinate status disagrees with traced modes")
    require(contract["mapping"] == {"file_offset": "0x238", "loaded_address": "0x0080E000"}, "production image map mismatch")
    service, write, reply, staging = (contract[k] for k in ("normal_service", "write", "reply", "staging"))
    suffix = "-224D-11E6-9FB8-0002A5D5C51B"
    require(service["service_uuid"] == "CBA20D00" + suffix and write["uuid"] == "CBA20002" + suffix
            and reply["uuid"] == "CBA20003" + suffix, "normal service/request/reply UUID mismatch")
    require(service["attribute_count"] == 6 and service["attribute_record_bytes"] == 28
            and service["attribute_table_bytes"] == service["attribute_count"] * service["attribute_record_bytes"],
            "attribute table geometry mismatch")
    require(service["excluded_bootstrap_result"] == 2 and service["service_id_address"] == "0x00208AAD"
            and service["callback_pointer_address"] == "0x002082CC", "normal profile registration scope mismatch")
    require(write["attribute_index"] == 2 and reply["attribute_index"] == 4 and reply["cccd_index"] == 5,
            "request/response characteristic index mismatch")
    require(write["declaration_properties_hex"] == "0C" and write["permission_word_hex"] == "00000010"
            and reply["declaration_properties_hex"] == "10" and reply["cccd_uuid_hex"] == "2902",
            "characteristic declaration/permission mismatch")
    require(reply["pdu_type"] == 0 and reply["body_is_dispatcher_output"] is True
            and reply["length_is_dispatcher_return_value"] is True and reply["added_prefix_hex"] == "",
            "response submission envelope mismatch")
    require(all(reply[key] is False for key in ("cccd_runtime_state_verified", "stack_acceptance_verified", "notification_delivery_verified")),
            "response submission must not assert delivery")
    require([staging[k] for k in ("pending_offset", "connection_offset", "length_offset", "frame_offset")] == [0, 1, 2, 3]
            and staging["cleared_frame_bytes"] == 247 and staging["copy_count_bits"] == 16
            and staging["copy_index_bits"] == 8 and staging["stored_length_bits"] == 8,
            "staging geometry/length representation mismatch")
    require(staging["busy_frame_copied"] is False and staging["busy_callback_result"] == 0,
            "busy write acceptance must not imply command copy")
    require(all(staging[k] is False for k in ("local_minimum_length_guard", "local_maximum_length_guard", "upstream_att_limits_verified", "large_write_admission_verified")),
            "local lengths must not invent runtime ATT bounds or admission")
    require(write["local_write_type_gate"] is False and write["local_length_gate"] is False,
            "write callback guard scope mismatch")
    require(staging["address"] == "0x002080CF" and staging["semaphore_address"] == "0x002092A4"
            and staging["requires_registered_service_id"] is True and staging["requires_empty_pending_slot"] is True,
            "staging registration/semaphore admission mismatch")
    require(contract["event"] == {"connection_offset": 0, "type_offset": 1, "type_hex": "03",
                                 "selector_offset": 4, "selector_hex": "01", "write_type_offset": 5,
                                 "length_offset": 6, "length_bytes": 2, "value_pointer_offset": 8, "value_pointer_bytes": 4},
            "forwarded event geometry mismatch")
    require(contract["dispatch"]["ext_receives_original_length"] is False
            and contract["dispatch"]["reply_initial_byte_hex"] == "01"
            and contract["dispatch"]["initialization_after_header_mode_acceptance"] is True,
            "EXT length/reply initialization mismatch")
    require(contract["header"]["combined_value"] == "a + b"
            and contract["modes"]["0"]["accepted_sums"] == [0, 2]
            and contract["modes"]["1"]["bypass_sums"] == [0], "mode sum predicates disagree")
    header = contract["header"]
    require([header[k] for k in ("class_mask", "ext_class", "reserved_mask", "mode_shift", "mode_mask")] == [15, 15, 192, 4, 3]
            and header["magic_hex"] == "57" and header["reserved_bits_reply_hex"] == "04"
            and header["invalid_magic_response_length"] == 0, "header masks/results mismatch")
    require([header[k] for k in ("flag_a_byte_offset", "flag_a_bit", "flag_b_byte_offset", "flag_b_bit")] == [16, 7, 17, 5]
            and header["configuration_address"] == "0x00207FC0" and header["configuration_meanings_verified"] is False,
            "configuration flag source/meaning mismatch")
    require([contract["modes"][str(m)]["rejected_reply_hex"] for m in range(4)] == ["07", "09", "0A", "0A"]
            and contract["modes"]["2"]["payload_offset"] is None and contract["modes"]["3"]["payload_offset"] is None,
            "mode rejection bodies/dispatch mismatch")
    mode1 = contract["modes"]["1"]
    require(mode1["comparison_helper"] == "0x008102AC" and mode1["check_length"] == 4
            and mode1["frame_check_offset"] == 2 and mode1["configuration_check_offset"] == 4
            and mode1["helper_equal_result"] == 1 and mode1["check_value_provisioning_verified"] is False,
            "mode-1 comparison or provisioning boundary mismatch")
    for mode, offset in ((0, 2), (1, 6)):
        require(contract["modes"][str(mode)]["payload_offset"] == main["coordinates"][f"prod_1_04_mode{mode}_payload_offset"] == offset,
                "main/production payload offset mismatch")
        layout = contract["layouts"][str(mode)]
        require(layout["set"]["payload_prefix_hex"] == main["set_peer"]["payload_prefix_hex"]
                and layout["clear"]["payload_hex"] == main["clear_peer"]["payload_hex"]
                and layout["getter"]["payload_prefix_hex"] == main["get_peer"]["prod_1_04"]["payload_prefix_hex"],
                "main/production payload prefix mismatch")
        require(layout["set"]["peer_frame_offset"] == offset + main["set_peer"]["payload_peer_offset"]
                and layout["set"]["ignored_frame_offset"] == offset + main["set_peer"]["ignored_byte"]["payload_offset"]
                and layout["set"]["peer_length"] == 6
                and layout["set"]["host_minimum_bytes"] == offset + 10, "production set field geometry mismatch")
        require(layout["clear"]["host_minimum_bytes"] == offset + 3, "production clear minimum mismatch")
        getter = layout["getter"]
        require(getter["required_frame_offset"] == offset + main["get_peer"]["prod_1_04"]["query_byte_offset"]
                and getter["ignored_frame_offset"] == offset + 2 and getter["required_byte_hex"] == "01"
                and getter["host_minimum_bytes"] == offset + 4, "production getter field geometry mismatch")
    require(main["get_peer"]["prod_1_04"]["full_frame_encoding_verified"] is True,
            "getter complete-frame evidence status mismatch")
    getter = main["get_peer"]["prod_1_04"]
    require(bytes.fromhex(getter["mode0_frame_hex"]) == bytes.fromhex("57 0F 59 0A 00 01")
            and getter["mode0_host_minimum_length"] == contract["layouts"]["0"]["getter"]["host_minimum_bytes"]
            and getter["mode1_host_minimum_length"] == contract["layouts"]["1"]["getter"]["host_minimum_bytes"],
            "main production getter complete example/minimum mismatch")
    coverage, seen = set(), set()
    def record(case):
        require(case["id"] not in seen, "duplicate production fixture: " + case["id"])
        seen.add(case["id"])
        counts["structural_cases"] += 1
    for case in fixtures["mode_cases"]:
        record(case)
        frame, check = bytes.fromhex(case["request_hex"]), bytes.fromhex(case["config_check4_hex"])
        offset, error = header_result(frame, case["config_bit_a"], case["config_bit_b"], check)
        require(case["ext_reached"] is (offset is not None) and case["payload_offset"] == offset,
                case["id"] + ": mode admission/payload mismatch")
        require(case["error_body_hex"] == (error.hex().upper() if error is not None else None),
                case["id"] + ": mode error body mismatch")
        mode = (frame[1] >> 4) & 3
        coverage.add((case["config_bit_a"], case["config_bit_b"], mode, frame[2:6] == check if mode == 1 else None))
    expected = {(a, b, mode, match) for a in (0, 1) for b in (0, 1)
                for mode in (0, 1, 2, 3) for match in ((False, True) if mode == 1 else (None,))}
    require(coverage == expected, "production mode truth table is incomplete")
    for case in fixtures["frame_cases"]:
        record(case)
        frame = bytes.fromhex(case["request_hex"])
        offset, error = header_result(frame, case["config_bit_a"], case["config_bit_b"], bytes.fromhex(case["config_check4_hex"]))
        kind = case["kind"]
        if kind == "header_rejection":
            require(offset is None and error == bytes.fromhex(case["expected_reply_hex"]), case["id"] + ": header rejection mismatch")
            continue
        require(offset is not None, case["id"] + ": operation fixture does not reach EXT")
        if offset is None:
            continue
        payload, state = frame[offset:], case["initial_state"]
        flag, connection = state["binding_flag"], int(state["connection_identifier_hex"], 16)
        mutation = False
        if kind == "set":
            require(payload[:3] == bytes.fromhex("58 0A 02") and len(payload) == 10, case["id"] + ": complete setter layout")
            mutation = not (flag == 1 and connection != 255)
            result = b"\x01" + payload[4:10] if mutation else b"\x02"
        elif kind == "clear":
            require(payload == bytes.fromhex("58 0A 01"), case["id"] + ": complete clear layout")
            mutation = flag != 0 or connection == 255
            result = b"\x01"
        elif kind == "getter":
            require(payload[:2] == bytes.fromhex("59 0A") and len(payload) == 4, case["id"] + ": complete getter layout")
            result = b"\x01\x20\x01" + bytes.fromhex(state["stored_peer_hex"]) + bytes.fromhex(state["local_source_2_to_7_hex"])[::-1] if payload[3] == 1 and (flag != 1 or connection == 255) else b"\x01"
        elif kind == "unsupported":
            require(payload[:2] == bytes.fromhex("58 0A") and len(payload) == 3 and payload[2] not in (1, 2), case["id"] + ": unsupported operation layout")
            result = bytes.fromhex(contract["dispatch"]["reply_initial_byte_hex"])
        else:
            require(False, case["id"] + ": unsupported production fixture kind")
            continue
        require(result == bytes.fromhex(case["expected_reply_hex"]) and case["expected_mutation"] is mutation,
                case["id"] + ": complete frame response/state mismatch")
    for case in fixtures["transport_cases"]:
        record(case)
        if case["kind"] == "short_frame":
            frame = bytes.fromhex(case["request_hex"])
            require(len(frame) == 11 and case["host_supplies_all_fields"] is False
                    and case["admission_assumed_only"] is True and case["hardware_observed"] is False,
                    case["id"] + ": short-frame evidence boundary")
            staged = frame + bytes(staging["cleared_frame_bytes"] - len(frame))
            require(staged[6:12] == bytes.fromhex(case["conditional_peer_hex"]), case["id"] + ": conditional short-frame copy")
        elif case["kind"] == "staging_admission":
            callback = 0x040A if case["attribute_index"] != write["attribute_index"] else 0x040D if not case["value_pointer_nonnull"] else 0
            copied = callback == 0 and case["service_id_matches"] and case["event_type"] == 3 and case["event_selector"] == 1 and case["pending"] == 0
            require(callback == int(case["expected_callback_result_hex"], 16) and case["frame_copied"] is copied
                    and case["command_execution_proven"] is False, case["id"] + ": admission/execution boundary")
        else:
            require(False, case["id"] + ": unknown transport fixture kind")
