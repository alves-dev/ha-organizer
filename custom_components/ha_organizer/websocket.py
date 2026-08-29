from __future__ import annotations

from copy import deepcopy
import math
import re

from homeassistant.components import websocket_api
from homeassistant.components.homeassistant.const import DATA_EXPOSED_ENTITIES
from homeassistant.components.homeassistant.exposed_entities import (
    KNOWN_ASSISTANTS,
    async_should_expose,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import category_registry as cr
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import label_registry as lr
from homeassistant.helpers.storage import Store
import voluptuous as vol

from .const import DEFAULT_CONFIG, DOMAIN, MODULES, VERSION
from .core import overview, scan

MAX_CATEGORY_NAME_LENGTH = 10000
MAX_NUMERIC_SETTING = 1000000
MAX_SCOPES = 3
MAX_DOMAIN_LENGTH = 64
MAX_PATTERN_LENGTH = 256
MAX_REVIEW_KEY_LENGTH = 1024
MAX_FINGERPRINT_LENGTH = 256
MAX_BATCH_REVIEWS = 500
ADMIN_REQUIRED = "Administrator required"


def _admin(connection):
    return connection.user and connection.user.is_admin


def _entity_area(areas_reg, device, entity):
    if entity.area_id:
        return areas_reg.async_get_area(entity.area_id)
    if device and device.area_id:
        return areas_reg.async_get_area(device.area_id)
    return None


def _device_integration(hass, device):
    entry_ids = sorted(getattr(device, "config_entries", ()) or ())
    if not getattr(hass, "config_entries", None):
        return {"integration": "unknown", "integration_name": "Unknown integration"}
    entries = [hass.config_entries.async_get_entry(entry_id) for entry_id in entry_ids]
    entry = next((candidate for candidate in entries if candidate), None)
    if not entry:
        return {"integration": "unknown", "integration_name": "Unknown integration"}
    return {
        "integration": entry.domain,
        "integration_name": entry.domain.replace("_", " ").title(),
    }


def _validate_categories(categories):
    if not isinstance(categories, dict):
        raise ValueError("categories must be an object")
    min_length = categories.get("min_length")
    if (
        not isinstance(min_length, (int, float))
        or isinstance(min_length, bool)
        or not math.isfinite(min_length)
        or min_length < 0
        or min_length > MAX_CATEGORY_NAME_LENGTH
    ):
        raise ValueError("categories.min_length must be a non-negative number")
    if categories.get("language") not in ("any", "pt-BR", "en", "es"):
        raise ValueError("categories.language is invalid")
    if categories.get("case_policy") not in ("any", "lowercase", "uppercase"):
        raise ValueError("categories.case_policy is invalid")


def _validate_boolean_settings(config):
    fields_by_section = {
        "categories": ("require_icon", "allow_spaces", "allow_punctuation"),
        "zones": (
            "detect_duplicate_geometry",
            "detect_overlapping_geometry",
            "require_icon",
        ),
        "labels": ("require_icon", "require_color"),
    }
    for section, fields in fields_by_section.items():
        if not isinstance(config.get(section), dict):
            raise ValueError(f"{section} must be an object")
        if any(not isinstance(config[section].get(field), bool) for field in fields):
            raise ValueError(f"{section} boolean settings are invalid")


def _validate_numeric_settings(config):
    fields_by_section = {
        "zones": ("min_name_length", "min_radius", "max_radius"),
        "labels": ("min_name_length", "min_description_length"),
    }
    for section, fields in fields_by_section.items():
        if not isinstance(config.get(section), dict):
            raise ValueError(f"{section} must be an object")
        for field in fields:
            value = config[section].get(field)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
                or value > MAX_NUMERIC_SETTING
            ):
                raise ValueError(f"{section}.{field} must be a non-negative number")


def _validate_zone_radii(zones):
    if zones["max_radius"] and zones["max_radius"] < zones["min_radius"]:
        raise ValueError(
            "zones.max_radius must be zero or greater than zones.min_radius"
        )


def _validate_zones(zones):
    if zones["case_policy"] not in ("any", "capitalized", "lowercase"):
        raise ValueError("zones.case_policy is invalid")
    _validate_zone_radii(zones)


def _validate_labels(labels):
    if not isinstance(labels, dict):
        raise ValueError("labels must be an object")
    if labels["min_name_length"] < 1:
        raise ValueError("labels.min_name_length must be at least 1")


def _validate_module_settings(modules):
    area_settings = modules.get("areas", {}).get("settings", {})
    if not isinstance(area_settings, dict):
        raise ValueError("modules.areas.settings must be an object")
    for field in ("require_floor", "require_aliases", "require_picture"):
        if field in area_settings and not isinstance(area_settings[field], bool):
            raise ValueError(f"modules.areas.settings.{field} must be boolean")
    if area_settings.get("case_policy", "any") not in (
        "any",
        "capitalized",
        "lowercase",
    ):
        raise ValueError("modules.areas.settings.case_policy is invalid")


def _validate_config_shape(config):  # noqa: PLR0912  # NOSONAR
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    modules = config.get("modules")
    if not isinstance(modules, dict):
        raise ValueError("modules must be an object")
    allowed_top_level = {
        "schema_version",
        "modules",
        "categories",
        "zones",
        "labels",
        "entity_id_pattern",
        "entity_id_mode",
        "excluded_domains",
        "normalization",
    }
    if any(key not in allowed_top_level for key in config):
        raise ValueError("config contains an unknown field")
    if any(module not in MODULES for module in modules):
        raise ValueError("config contains an unknown module")
    for module, options in modules.items():
        if not isinstance(options, dict):
            raise ValueError(f"modules.{module} must be an object")
        if not isinstance(options.get("enabled", True), bool):
            raise ValueError(f"modules.{module}.enabled must be boolean")
        if "settings" in options and not isinstance(options["settings"], dict):
            raise ValueError(f"modules.{module}.settings must be an object")
    _validate_module_settings(modules)
    scopes = config.get("categories", {}).get("scopes")
    if not isinstance(scopes, list) or any(
        scope not in ("automation", "script", "scene") for scope in scopes
    ):
        raise ValueError("categories.scopes is invalid")
    if len(scopes) > MAX_SCOPES:
        raise ValueError("categories.scopes has too many entries")
    excluded = config.get("excluded_domains", [])
    if not isinstance(excluded, list) or any(
        not isinstance(domain, str)
        or len(domain) > MAX_DOMAIN_LENGTH
        or not re.fullmatch(r"[a-z0-9_]+", domain)
        for domain in excluded
    ):
        raise ValueError("excluded_domains is invalid")
    pattern = config.get("entity_id_pattern")
    if (
        not isinstance(pattern, str)
        or not pattern.strip()
        or len(pattern) > MAX_PATTERN_LENGTH
    ):
        raise ValueError("entity_id_pattern is invalid")
    for normalization in [
        config.get("normalization", {}),
        config.get("categories", {}).get("normalization", {}),
        config.get("zones", {}).get("normalization", {}),
        *(
            options.get("settings", {}).get("normalization", {})
            for options in modules.values()
        ),
    ]:
        if not isinstance(normalization, dict) or any(
            key not in ("case_insensitive", "ignore_accents", "normalize_separators")
            or not isinstance(value, bool)
            for key, value in normalization.items()
        ):
            raise ValueError("normalization settings are invalid")


def _merge_config(incoming):
    if not isinstance(incoming, dict):
        raise ValueError("config must be an object")
    for section in ("modules", "categories", "zones", "labels"):
        if section in incoming and not isinstance(incoming[section], dict):
            raise ValueError(f"{section} must be an object")
    config = deepcopy(DEFAULT_CONFIG)
    config.update(incoming)
    config["modules"] = {**DEFAULT_CONFIG["modules"], **incoming.get("modules", {})}
    config["categories"] = {
        **DEFAULT_CONFIG["categories"],
        **incoming.get("categories", {}),
    }
    config["zones"] = {**DEFAULT_CONFIG["zones"], **incoming.get("zones", {})}
    config["labels"] = {**DEFAULT_CONFIG["labels"], **incoming.get("labels", {})}
    _validate_config_shape(config)
    _validate_categories(config["categories"])
    _validate_boolean_settings(config)
    _validate_numeric_settings(config)
    _validate_zones(config["zones"])
    _validate_labels(config["labels"])
    return config


async def _store(hass):
    store = Store(hass, VERSION, f"{DOMAIN}.data", private=True)
    data = await store.async_load()
    if data:
        config = data.get("config", {})
        data["config"] = _merge_config(config)
        return store, data
    return store, {
        "schema_version": VERSION,
        "config": DEFAULT_CONFIG.copy(),
        "reviews": {},
        "last_scan": None,
    }


def _snapshot(hass):  # noqa: PLR0912  # NOSONAR
    areas_reg = ar.async_get(hass)
    devices_reg = dr.async_get(hass)
    entities_reg = er.async_get(hass)
    devices_by_area = {}
    for device in devices_reg.devices.values():
        if device.area_id:
            devices_by_area.setdefault(device.area_id, []).append(device)
    entities_by_area = {}
    entities_by_device = {}

    for entity in entities_reg.entities.values():
        device = devices_reg.async_get(entity.device_id) if entity.device_id else None
        if device:
            entities_by_device.setdefault(device.id, []).append(entity.entity_id)
        area = _entity_area(areas_reg, device, entity)
        if area:
            entities_by_area.setdefault(area.id, []).append(entity.entity_id)
    areas = []
    for area in areas_reg.areas.values():
        area_devices = devices_by_area.get(area.id, [])
        devices = [d.id for d in area_devices]
        entities = entities_by_area.get(area.id, [])
        areas.append(
            {
                "id": area.id,
                "name": area.name,
                "floor": getattr(area, "floor", None),
                "icon": getattr(area, "icon", None),
                "picture": getattr(area, "picture", None),
                "aliases": list(getattr(area, "aliases", ()) or ()),
                "devices": devices,
                "device_details": [
                    {
                        "id": d.id,
                        "name": d.name_by_user or d.name,
                        **_device_integration(hass, d),
                        "entity_ids": sorted(entities_by_device.get(d.id, [])),
                    }
                    for d in area_devices
                ],
                "entities": entities,
            }
        )
    devices_without_area = [
        {
            "id": d.id,
            "name": d.name_by_user or d.name,
            **_device_integration(hass, d),
            "entity_ids": sorted(entities_by_device.get(d.id, [])),
        }
        for d in devices_reg.devices.values()
        if not d.area_id
    ]
    entities = []
    for e in entities_reg.entities.values():
        device = devices_reg.async_get(e.device_id) if e.device_id else None
        area = _entity_area(areas_reg, device, e)
        entities.append(
            {
                "entity_id": e.entity_id,
                "name": e.name or e.original_name,
                "area_id": area.id if area else None,
                "area_name": area.name if area else None,
                "device_id": e.device_id,
                "device_name": device.name if device else None,
                "platform": e.platform,
            }
        )
    zones = []
    for state in hass.states.async_all("zone"):
        attrs = state.attributes
        zones.append(
            {
                "id": state.entity_id.split(".", 1)[-1],
                "name": attrs.get("friendly_name", state.name),
                "latitude": attrs.get("latitude"),
                "longitude": attrs.get("longitude"),
                "radius": attrs.get("radius"),
                "passive": attrs.get("passive", False),
                "icon": attrs.get("icon"),
            }
        )
    exposed = []
    exposed_entities = hass.data.get(DATA_EXPOSED_ENTITIES)
    if exposed_entities is not None:
        # The exposed-entities store only contains legacy entries. Registry
        # options are the source of truth for entities with a unique_id, so
        # inspect every known entity and let HA resolve both storage paths.
        entity_ids = set(entities_reg.entities)
        entity_ids.update(hass.states.async_entity_ids())
        for entity_id in sorted(entity_ids):
            assistants = {
                assistant
                for assistant in KNOWN_ASSISTANTS
                if async_should_expose(hass, assistant, entity_id)
            }
            if assistants:
                state = hass.states.get(entity_id)
                registry_entry = entities_reg.async_get(entity_id)
                exposed.append(
                    {
                        "entity_id": entity_id,
                        "name": (registry_entry.name if registry_entry else None)
                        or (state.attributes.get("friendly_name") if state else None)
                        or entity_id,
                        "aliases": [
                            alias
                            for alias in (registry_entry.aliases or [])
                            if isinstance(alias, str)
                        ]
                        if registry_entry
                        else [],
                        "assistants": sorted(assistants),
                    }
                )
    categories = {}
    category_registry = cr.async_get(hass)
    category_entities = {scope: {} for scope in ("automation", "script", "scene")}
    for entry in entities_reg.entities.values():
        for scope, category_id in entry.categories.items():
            if scope in category_entities:
                category_entities[scope].setdefault(category_id, []).append(
                    entry.entity_id
                )
    for scope in ("automation", "script", "scene"):
        scope_categories = []
        for category in category_registry.async_list_categories(scope=scope):
            resources = sorted(category_entities[scope].get(category.category_id, []))
            scope_categories.append(
                {
                    "id": category.category_id,
                    "name": category.name,
                    "icon": category.icon,
                    "entities": resources,
                }
            )
        categories[scope] = scope_categories
    labels = []
    label_registry = lr.async_get(hass)
    for label in label_registry.labels.values():
        labels.append(
            {
                "id": label.label_id,
                "name": label.name,
                "description": getattr(label, "description", None),
                "icon": getattr(label, "icon", None),
                "color": getattr(label, "color", None),
            }
        )

    return {
        "areas": areas,
        "devices_without_area": devices_without_area,
        "entities": entities,
        "zones": zones,
        "categories": categories,
        "labels": labels,
        "exposed": exposed,
    }


@callback
def async_register_websocket_commands(hass: HomeAssistant):  # noqa: PLR0915  # NOSONAR
    @websocket_api.websocket_command({"type": "ha_organizer/config/get"})
    @websocket_api.async_response
    async def config_get(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        _, data = await _store(hass)
        connection.send_result(msg["id"], data.get("config", DEFAULT_CONFIG))

    @websocket_api.websocket_command(
        {"type": "ha_organizer/config/update", "config": dict}
    )
    @websocket_api.async_response
    async def config_update(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        store, data = await _store(hass)
        incoming = msg["config"]
        try:
            data["config"] = _merge_config(incoming)
        except ValueError as error:
            return connection.send_error(msg["id"], "invalid_config", str(error))
        await store.async_save(data)
        connection.send_result(msg["id"], data["config"])

    @websocket_api.websocket_command({"type": "ha_organizer/reviews/reset"})
    @websocket_api.async_response
    async def reviews_reset(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        store, data = await _store(hass)
        data["reviews"] = {}
        data["last_scan"] = None
        await store.async_save(data)
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command({"type": "ha_organizer/config/reset"})
    @websocket_api.async_response
    async def config_reset(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        store, data = await _store(hass)
        data["config"] = deepcopy(DEFAULT_CONFIG)
        data["last_scan"] = None
        await store.async_save(data)
        connection.send_result(msg["id"], data["config"])

    @websocket_api.websocket_command({"type": "ha_organizer/scan"})
    @websocket_api.async_response
    async def do_scan(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        store, data = await _store(hass)
        result = scan(
            _snapshot(hass), data.get("config", DEFAULT_CONFIG), data.get("reviews", {})
        )
        data["last_scan"] = result
        await store.async_save(data)
        connection.send_result(msg["id"], result)

    @websocket_api.websocket_command(
        {
            "type": "ha_organizer/review/set",
            "item_key": vol.All(str, vol.Length(max=1024)),
            "status": str,
            "fingerprint": vol.All(str, vol.Length(max=MAX_FINGERPRINT_LENGTH)),
            vol.Optional("note", default=None): vol.Any(
                vol.All(str, vol.Length(max=2000)), None
            ),
        }
    )
    @websocket_api.async_response
    async def review_set(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        store, data = await _store(hass)
        status = msg["status"]
        if status not in ("reviewed", "ignored", "pending"):
            return connection.send_error(
                msg["id"], "invalid_status", "Invalid review status"
            )
        if (
            len(msg["item_key"]) > MAX_REVIEW_KEY_LENGTH
            or len(msg["fingerprint"]) > MAX_FINGERPRINT_LENGTH
        ):
            return connection.send_error(
                msg["id"], "invalid_review", "Review identifiers are too long"
            )
        if status == "pending":
            data["reviews"].pop(msg["item_key"], None)
        else:
            data["reviews"][msg["item_key"]] = {
                "review_status": status,
                "reviewed_fingerprint": msg["fingerprint"],
                "note": msg.get("note"),
            }
        await store.async_save(data)
        connection.send_result(msg["id"], {"ok": True})

    @websocket_api.websocket_command(
        {
            "type": "ha_organizer/reviews/batch_set",
            "status": str,
            "items": list,
        }
    )
    @websocket_api.async_response
    async def reviews_batch_set(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        status = msg["status"]
        items = msg["items"]
        if status not in ("reviewed", "ignored", "pending"):
            return connection.send_error(
                msg["id"], "invalid_status", "Invalid review status"
            )
        if not items or len(items) > MAX_BATCH_REVIEWS:
            return connection.send_error(
                msg["id"], "invalid_review", "Review batch size is invalid"
            )
        for item in items:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("item_key"), str)
                or not isinstance(item.get("fingerprint"), str)
                or len(item["item_key"]) > MAX_REVIEW_KEY_LENGTH
                or len(item["fingerprint"]) > MAX_FINGERPRINT_LENGTH
            ):
                return connection.send_error(
                    msg["id"], "invalid_review", "Review identifiers are invalid"
                )
        store, data = await _store(hass)
        for item in items:
            if status == "pending":
                data["reviews"].pop(item["item_key"], None)
            else:
                data["reviews"][item["item_key"]] = {
                    "review_status": status,
                    "reviewed_fingerprint": item["fingerprint"],
                    "note": None,
                }
        await store.async_save(data)
        connection.send_result(msg["id"], {"ok": True, "count": len(items)})

    @websocket_api.websocket_command({"type": "ha_organizer/overview"})
    @websocket_api.async_response
    async def get_overview(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
        _, data = await _store(hass)
        connection.send_result(
            msg["id"], overview(data.get("last_scan") or {"modules": {}})
        )

    # The decorator validates command messages; registration is explicit in the
    # WebSocket API and is required for the command to be discoverable.
    for command in (
        config_get,
        config_update,
        reviews_reset,
        config_reset,
        do_scan,
        review_set,
        reviews_batch_set,
        get_overview,
    ):
        websocket_api.async_register_command(hass, command)
