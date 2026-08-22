from __future__ import annotations

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

from .const import DEFAULT_CONFIG, DOMAIN, VERSION
from .core import overview, scan


def _admin(connection):
    return connection.user and connection.user.is_admin


async def _store(hass):
    store = Store(hass, VERSION, f"{DOMAIN}.data", private=True)
    data = await store.async_load()
    if data:
        config = data.get("config", {})
        data["config"] = {
            **DEFAULT_CONFIG,
            **config,
            "modules": {**DEFAULT_CONFIG["modules"], **config.get("modules", {})},
        }
        return store, data
    return store, {
        "schema_version": VERSION,
        "config": DEFAULT_CONFIG.copy(),
        "reviews": {},
        "last_scan": None,
    }


def _snapshot(hass):
    areas_reg = ar.async_get(hass)
    devices_reg = dr.async_get(hass)
    entities_reg = er.async_get(hass)
    areas = []
    for area in areas_reg.areas.values():
        devices = [d.id for d in devices_reg.devices.values() if d.area_id == area.id]
        entities = [
            e.entity_id
            for e in entities_reg.entities.values()
            if e.area_id == area.id or e.device_id in devices
        ]
        areas.append(
            {
                "id": area.id,
                "name": area.name,
                "floor": getattr(area, "floor", None),
                "devices": devices,
                "entities": entities,
            }
        )
    devices_without_area = [
        {"id": d.id, "name": d.name_by_user or d.name}
        for d in devices_reg.devices.values()
        if not d.area_id
    ]
    entities = []
    for e in entities_reg.entities.values():
        device = devices_reg.async_get(e.device_id) if e.device_id else None
        area = (
            areas_reg.async_get_area(e.area_id)
            if e.area_id
            else (
                areas_reg.async_get_area(device.area_id)
                if device and device.area_id
                else None
            )
        )
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
        entity_ids = set(exposed_entities.entities)
        entity_ids.update(entities_reg.entities)
        for entity_id in sorted(entity_ids):
            assistants = {
                assistant
                for assistant in KNOWN_ASSISTANTS
                if async_should_expose(hass, assistant, entity_id)
            }
            if assistants:
                exposed.append(
                    {"entity_id": entity_id, "assistants": sorted(assistants)}
                )
    categories = {}
    category_registry = cr.async_get(hass)
    for scope in ("automation", "script"):
        scope_categories = []
        for category in category_registry.async_list_categories(scope=scope):
            resources = [
                entry.entity_id
                for entry in entities_reg.entities.values()
                if entry.categories.get(scope) == category.category_id
            ]
            scope_categories.append(
                {
                    "id": category.category_id,
                    "name": category.name,
                    "icon": category.icon,
                    "entities": sorted(resources),
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
def async_register_websocket_commands(hass: HomeAssistant):
    @websocket_api.websocket_command({"type": "ha_organizer/config/get"})
    @websocket_api.async_response
    async def config_get(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(
                msg["id"], "not_allowed", "Administrator required"
            )
        _, data = await _store(hass)
        connection.send_result(msg["id"], data.get("config", DEFAULT_CONFIG))

    @websocket_api.websocket_command(
        {"type": "ha_organizer/config/update", "config": dict}
    )
    @websocket_api.async_response
    async def config_update(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(
                msg["id"], "not_allowed", "Administrator required"
            )
        store, data = await _store(hass)
        incoming = msg["config"]
        data["config"] = {
            **DEFAULT_CONFIG,
            **incoming,
            "modules": {**DEFAULT_CONFIG["modules"], **incoming.get("modules", {})},
        }
        await store.async_save(data)
        connection.send_result(msg["id"], data["config"])

    @websocket_api.websocket_command({"type": "ha_organizer/scan"})
    @websocket_api.async_response
    async def do_scan(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(
                msg["id"], "not_allowed", "Administrator required"
            )
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
            "item_key": str,
            "status": str,
            "fingerprint": str,
            vol.Optional("note", default=None): vol.Any(str, None),
        }
    )
    @websocket_api.async_response
    async def review_set(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(
                msg["id"], "not_allowed", "Administrator required"
            )
        store, data = await _store(hass)
        status = msg["status"]
        if status not in ("reviewed", "ignored", "pending"):
            return connection.send_error(
                msg["id"], "invalid_status", "Invalid review status"
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

    @websocket_api.websocket_command({"type": "ha_organizer/overview"})
    @websocket_api.async_response
    async def get_overview(hass, connection, msg):
        if not _admin(connection):
            return connection.send_error(
                msg["id"], "not_allowed", "Administrator required"
            )
        _, data = await _store(hass)
        connection.send_result(
            msg["id"], overview(data.get("last_scan") or {"modules": {}})
        )

    # The decorator validates command messages; registration is explicit in the
    # WebSocket API and is required for the command to be discoverable.
    for command in (config_get, config_update, do_scan, review_set, get_overview):
        websocket_api.async_register_command(hass, command)
