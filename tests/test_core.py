from custom_components.ha_organizer.core import (
    apply_reviews,
    fingerprint,
    normalize,
    overview,
    scan,
)


def test_normalization_handles_accents_and_separators():
    assert normalize("Luz-do_escritório") == "luz do escritorio"


def test_fingerprint_is_stable_for_set_order():
    assert fingerprint("x", "y", {"values": {"a", "b"}}) == fingerprint(
        "x", "y", {"values": {"b", "a"}}
    )


def test_categories_and_review_become_stale_after_change():
    config = {
        "modules": {
            "categories": {
                "enabled": True,
                "settings": {"scopes": ["automation", "script"]},
            }
        }
    }
    first = scan(
        {"categories": {"automation": ["Security"], "script": ["Security"]}}, config
    )
    item = first["modules"]["categories"][0]
    reviewed = {
        item["item_key"]: {
            "review_status": "reviewed",
            "reviewed_fingerprint": item["fingerprint"],
        }
    }
    second = scan(
        {"categories": {"automation": ["Security"], "script": []}}, config, reviewed
    )
    assert second["modules"]["categories"][0]["compliance_status"] == "attention"
    assert second["modules"]["categories"][0]["review_status"] == "stale"


def test_review_and_compliance_are_independent():
    items = apply_reviews(
        [{"item_key": "x", "fingerprint": "f", "compliance_status": "compliant"}],
        {"x": {"review_status": "reviewed", "reviewed_fingerprint": "f"}},
    )
    assert (
        items[0]["compliance_status"] == "compliant"
        and items[0]["review_status"] == "reviewed"
    )


def test_exposed_collisions_are_grouped():
    result = scan(
        {
            "exposed": [
                {"entity_id": "light.one", "name": "Luz do Escritório"},
                {"entity_id": "light.two", "aliases": ["luz-do escritorio"]},
            ]
        },
        {"modules": {"exposed": {"enabled": True}}},
    )
    assert len(result["modules"]["exposed"]) == 1
    assert result["modules"]["exposed"][0]["compliance_status"] == "non_compliant"


def test_overview_has_separate_counters():
    data = overview(
        {
            "modules": {
                "x": [{"review_status": "pending", "compliance_status": "compliant"}]
            }
        }
    )
    assert data["review"]["pending"] == 1 and data["compliance"]["compliant"] == 1
