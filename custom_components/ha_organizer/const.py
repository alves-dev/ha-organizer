DOMAIN = "ha_organizer"
NAME = "HA Organizer"
VERSION = 1
MODULES = ("categories", "areas", "zones", "labels", "entity_ids", "exposed")
DEFAULT_MODULES = {module: {"enabled": True} for module in MODULES}
DEFAULT_CONFIG = {
    "schema_version": VERSION,
    "modules": DEFAULT_MODULES,
    "categories": {
        "scopes": ["automation", "script"],
        "require_icon": False,
        "min_length": 0,
        "language": "any",
        "case_policy": "any",
        "allow_spaces": True,
        "allow_punctuation": True,
    },
    "zones": {
        "detect_duplicate_geometry": True,
        "detect_overlapping_geometry": True,
        "min_radius": 0,
        "max_radius": 0,
        "require_icon": False,
    },
    "labels": {
        "min_name_length": 1,
        "min_description_length": 0,
        "require_icon": False,
        "require_color": False,
    },
    "entity_id_pattern": "{domain}.{area}_{device}_{entity}",
    "entity_id_mode": "builder",
    "excluded_domains": [],
    "normalization": {
        "case_insensitive": True,
        "ignore_accents": True,
        "normalize_separators": True,
    },
}
