from custom_components.ha_organizer.core import (
    areas,
    categories,
    entity_ids,
    labels,
    scan,
    zones,
)


def test_categories_applies_all_policies_and_comparison_findings():
    rows = categories(
        {
            "categories": {
                "automation": [{"name": "Room Name", "icon": "mdi:home"}],
                "script": [{"name": "room_name", "icon": "mdi:star"}],
            }
        },
        {
            "scopes": ["automation", "script", "missing"],
            "require_icon": True,
            "min_length": 10,
            "language": "en",
            "case_policy": "lowercase",
            "allow_spaces": False,
            "allow_punctuation": False,
        },
    )
    finding_ids = {finding["rule_id"] for finding in rows[0]["findings"]}
    assert {
        "category_name_variants",
        "category_required_in_selected_scopes",
        "category_icon_variants",
        "category_min_length",
        "category_case_policy",
        "category_spaces_policy",
        } <= finding_ids
    punctuation = categories(
        {"categories": {"automation": ["Room!"]}},
        {"allow_punctuation": False},
    )
    assert any(
        finding["rule_id"] == "category_punctuation_policy"
        for finding in punctuation[0]["findings"]
    )


def test_categories_can_keep_scopes_independent():
    rows = categories(
        {"categories": {"automation": ["Build"], "script": ["Build"]}},
        {"compare": False, "scopes": ["automation", "script"]},
    )
    assert len(rows) == len({"automation", "script"})
    assert all(not row["findings"] for row in rows)


def test_categories_checks_icon_uppercase_and_language_rules():
    rows = categories(
        {"categories": {"automation": ["UPPER"]}},
        {"require_icon": True, "case_policy": "uppercase"},
    )
    assert any(
        finding["rule_id"] == "category_icon_required"
        for finding in rows[0]["findings"]
    )
    rows = categories(
        {"categories": {"automation": ["房间"]}},
        {"language": "en"},
    )
    assert any(
        finding["rule_id"] == "category_language_policy"
        for finding in rows[0]["findings"]
    )


def test_scan_merges_module_settings_and_skips_invalid_exposed_rows():
    result = scan(
        {"exposed": [{"entity_id": "", "name": "ignored"}]},
        {
            "categories": {"min_length": 2},
            "zones": {"min_radius": 1},
            "labels": {"min_name_length": 2},
            "entity_id_pattern": "{domain}.{entity}",
            "modules": {
                "categories": {"enabled": False},
                "zones": {"enabled": False},
                "labels": {"enabled": False},
                "entity_ids": {"enabled": False},
                "exposed": {"enabled": True},
            },
        },
    )
    assert result["modules"]["exposed"] == []


def test_areas_detect_duplicate_names_and_devices_without_area():
    rows = areas(
        {
            "areas": [
                {"id": "a", "name": "Living Room", "devices": ["d"]},
                {"id": "b", "name": "living-room"},
            ],
            "devices_without_area": [{"id": "orphan", "name": "Orphan"}],
        }
    )
    assert rows[0]["compliance_status"] == "non_compliant"
    assert rows[-1]["item_key"] == "areas:device:orphan"


def test_areas_apply_metadata_and_case_policies():
    rows = areas(
        {"areas": [{"id": "office", "name": "office"}]},
        {
            "require_floor": True,
            "require_aliases": True,
            "require_picture": True,
            "case_policy": "capitalized",
        },
    )
    assert {finding["rule_id"] for finding in rows[0]["findings"]} == {
        "area_floor_required",
        "area_aliases_required",
        "area_picture_required",
        "area_case_policy",
    }
    compound_name = areas(
        {"areas": [{"id": "couple", "name": "Quarto Casal"}]},
        {"case_policy": "capitalized"},
    )
    assert not compound_name[0]["findings"]
    lowercase = areas(
        {"areas": [{"id": "office", "name": "Office"}]},
        {"case_policy": "lowercase"},
    )
    assert lowercase[0]["findings"][0]["rule_id"] == "area_case_policy"


def test_zones_detect_geometry_and_policy_findings_but_not_home_duplicates():
    rows = zones(
        {
            "zones": [
                {
                    "id": "home",
                    "name": "Home",
                    "latitude": 1,
                    "longitude": 2,
                    "radius": 5,
                },
                {
                    "id": "office",
                    "name": "",
                    "latitude": 1,
                    "longitude": 2,
                    "radius": 5,
                },
            ]
        },
        {"require_icon": True, "min_radius": 10, "max_radius": 4},
    )
    assert not any(
        f["rule_id"] == "duplicate_zone_geometry" for f in rows[0]["findings"]
    )
    assert rows[1]["compliance_status"] == "non_compliant"
    assert {f["rule_id"] for f in rows[1]["findings"]} >= {
        "duplicate_zone_geometry",
        "zone_name_missing",
        "zone_icon_required",
        "zone_min_radius",
        "zone_max_radius",
    }


def test_zones_apply_name_length_and_case_policies():
    rows = zones(
        {"zones": [{"id": "office", "name": "a"}]},
        {"min_name_length": 2, "case_policy": "capitalized"},
    )
    assert {finding["rule_id"] for finding in rows[0]["findings"]} == {
        "zone_name_length",
        "zone_case_policy",
    }
    compound_name = zones(
        {"zones": [{"id": "couple", "name": "Quarto Casal"}]},
        {"case_policy": "capitalized"},
    )
    assert not compound_name[0]["findings"]
    lowercase = zones(
        {"zones": [{"id": "office", "name": "Office"}]},
        {"case_policy": "lowercase"},
    )
    assert lowercase[0]["findings"][0]["rule_id"] == "zone_case_policy"


def test_labels_detect_short_descriptions_and_duplicates():
    rows = labels(
        {
            "labels": [
                {"id": "one", "name": "A", "description": ""},
                {"id": "two", "name": "a", "description": "ok"},
            ]
        },
        {"min_name_length": 2, "min_description_length": 3},
    )
    assert all(row["compliance_status"] == "non_compliant" for row in rows)
    assert any(f["rule_id"] == "duplicate_label_name" for f in rows[0]["findings"])


def test_labels_apply_icon_and_color_policies():
    rows = labels(
        {"labels": [{"id": "living_room", "name": "Living Room"}]},
        {"require_icon": True, "require_color": True},
    )
    assert {finding["rule_id"] for finding in rows[0]["findings"]} == {
        "label_icon_required",
        "label_color_required",
    }


def test_entity_ids_check_format_pattern_and_exclusions():
    rows = entity_ids(
        {
            "entities": [
                {
                    "entity_id": "light.living_room_1",
                    "area_name": "Living Room",
                    "device_name": "Lamp",
                },
                {
                    "entity_id": "sensor.good",
                    "area_name": "Area",
                    "device_name": "Device",
                },
                {"entity_id": "broken", "area_name": None, "device_name": None},
                {"entity_id": "switch.any", "area_name": "A", "device_name": "D"},
            ]
        },
        {
            "pattern": "{domain}.{area}_{device}_{entity}",
            "excluded_domains": ["switch"],
        },
    )
    assert any(f["rule_id"] == "entity_id_format" for f in rows[0]["findings"])
    assert any(f["rule_id"] == "entity_id_pattern" for f in rows[1]["findings"])
    assert rows[2]["findings"]
    assert rows[3]["findings"] == []
