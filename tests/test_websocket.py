from types import SimpleNamespace

import pytest

from custom_components.ha_organizer import websocket
from custom_components.ha_organizer.const import DEFAULT_CONFIG, VERSION

MIN_LENGTH = 2
MIN_RESULTS = 6


def test_merge_config_accepts_and_rejects_policy_values():
    config = websocket._merge_config(DEFAULT_CONFIG)
    assert config["categories"]["language"] == "any"
    for invalid in (
        {"categories": {"min_length": -1}},
        {"categories": {"language": "fr"}},
        {"categories": {"case_policy": "mixed"}},
        {"categories": {"allow_spaces": "yes"}},
        {"zones": {"min_radius": -1}},
        {"zones": {"min_name_length": -1}},
        {"zones": {"case_policy": "mixed"}},
        {"zones": {"max_radius": 10, "min_radius": 20}},
        {"labels": {"min_name_length": 0}},
    ):
        with pytest.raises(ValueError):
            websocket._merge_config(invalid)


class FakeStore:
    data = None

    def __init__(self, *args, **kwargs):
        pass

    async def async_load(self):
        return self.data

    async def async_save(self, data):
        type(self).data = data


class FakeConnection:
    def __init__(self, is_admin=True):
        self.user = SimpleNamespace(is_admin=is_admin)
        self.results = []
        self.errors = []

    def send_result(self, msg_id, result):
        self.results.append((msg_id, result))

    def send_error(self, msg_id, code, message):
        self.errors.append((msg_id, code, message))


@pytest.mark.asyncio
async def test_websocket_commands_handle_admin_workflow(monkeypatch):
    commands = []
    monkeypatch.setattr(
        websocket.websocket_api,
        "async_register_command",
        lambda hass, command: commands.append(command),
    )
    monkeypatch.setattr(websocket, "Store", FakeStore)
    monkeypatch.setattr(
        websocket,
        "_snapshot",
        lambda hass: {"categories": {}, "areas": [], "zones": [], "labels": []},
    )
    monkeypatch.setattr(websocket, "scan", lambda *args: {"modules": {}})
    hass = SimpleNamespace()
    websocket.async_register_websocket_commands(hass)
    handlers = {command.__name__: command.__wrapped__ for command in commands}

    denied = FakeConnection(False)
    await handlers["config_get"](hass, denied, {"id": 1})
    denied_commands = (
        "config_update",
        "reviews_reset",
        "config_reset",
        "do_scan",
        "review_set",
        "reviews_batch_set",
        "get_overview",
    )
    denied_message = {
        "config": DEFAULT_CONFIG,
        "status": "pending",
        "item_key": "x",
        "fingerprint": "f",
    }
    for index, name in enumerate(denied_commands, start=20):
        await handlers[name](hass, denied, {"id": index, **denied_message})
    assert denied.errors[0][1] == "not_allowed"

    connection = FakeConnection()
    await handlers["config_get"](hass, connection, {"id": 2})
    await handlers["config_update"](
        hass,
        connection,
        {"id": 3, "config": DEFAULT_CONFIG},
    )
    await handlers["config_update"](
        hass,
        connection,
        {"id": 4, "config": {"categories": {"language": "invalid"}}},
    )
    assert any(error[1] == "invalid_config" for error in connection.errors)

    await handlers["review_set"](
        hass,
        connection,
        {"id": 5, "item_key": "x", "status": "reviewed", "fingerprint": "f"},
    )
    await handlers["review_set"](
        hass,
        connection,
        {"id": 6, "item_key": "x", "status": "pending", "fingerprint": "f"},
    )
    await handlers["review_set"](
        hass,
        connection,
        {"id": 7, "item_key": "x", "status": "bad", "fingerprint": "f"},
    )
    await handlers["reviews_batch_set"](
        hass,
        connection,
        {
            "id": 71,
            "status": "ignored",
            "items": [
                {"item_key": "area:one", "fingerprint": "first"},
                {"item_key": "area:two", "fingerprint": "second"},
            ],
        },
    )
    await handlers["reviews_batch_set"](
        hass,
        connection,
        {"id": 72, "status": "ignored", "items": []},
    )
    await handlers["reviews_reset"](hass, connection, {"id": 8})
    await handlers["config_reset"](hass, connection, {"id": 9})
    await handlers["do_scan"](hass, connection, {"id": 10})
    await handlers["get_overview"](hass, connection, {"id": 11})
    assert any(error[1] == "invalid_status" for error in connection.errors)
    assert any(error[1] == "invalid_review" for error in connection.errors)
    assert len(connection.results) >= MIN_RESULTS


@pytest.mark.asyncio
async def test_store_defaults_and_merges_existing_data(monkeypatch):
    monkeypatch.setattr(websocket, "Store", FakeStore)
    FakeStore.data = None
    _, fresh = await websocket._store(SimpleNamespace())
    assert fresh["schema_version"] == VERSION
    FakeStore.data = {
        "config": {"categories": {"min_length": MIN_LENGTH}},
        "reviews": {},
    }
    _, loaded = await websocket._store(SimpleNamespace())
    assert loaded["config"]["categories"]["min_length"] == MIN_LENGTH


def test_snapshot_collects_registry_data_and_exposure(monkeypatch):
    area = SimpleNamespace(
        id="office",
        name="Office",
        floor="ground",
        icon="mdi:desk",
        picture=None,
        aliases=("Study",),
    )
    assigned_device = SimpleNamespace(
        id="device-1",
        area_id="office",
        name_by_user=None,
        name="Desk Lamp",
        config_entries=("entry-1",),
    )
    unassigned_device = SimpleNamespace(
        id="device-2",
        area_id=None,
        name_by_user="Virtual Device",
        name="Unused name",
        config_entries=(),
    )
    assigned_entity = SimpleNamespace(
        entity_id="light.desk",
        device_id="device-1",
        area_id=None,
        name="Desk light",
        original_name="Desk light original",
        platform="demo",
        aliases=("Desk", 1),
        categories={"automation": "lighting"},
    )
    standalone_entity = SimpleNamespace(
        entity_id="sensor.outside",
        device_id=None,
        area_id="office",
        name=None,
        original_name="Outside sensor",
        platform="demo",
        aliases=(),
        categories={"script": "sensors", "unsupported": "ignored"},
    )
    areas_registry = SimpleNamespace(
        areas={area.id: area},
        async_get_area={area.id: area}.get,
    )
    devices = {
        assigned_device.id: assigned_device,
        unassigned_device.id: unassigned_device,
    }
    devices_registry = SimpleNamespace(
        devices=devices,
        async_get=devices.get,
    )
    entities = {
        assigned_entity.entity_id: assigned_entity,
        standalone_entity.entity_id: standalone_entity,
    }
    entities_registry = SimpleNamespace(
        entities=entities,
        async_get=entities.get,
    )
    category_registry = SimpleNamespace(
        async_list_categories=lambda scope: {
            "automation": [
                SimpleNamespace(
                    category_id="lighting", name="Lighting", icon="mdi:light"
                )
            ],
            "script": [
                SimpleNamespace(category_id="sensors", name="Sensors", icon=None)
            ],
            "scene": [],
        }[scope]
    )
    label_registry = SimpleNamespace(
        labels={
            "label-1": SimpleNamespace(
                label_id="label-1",
                name="Important",
                description="Priority devices",
                icon="mdi:star",
                color="red",
            )
        }
    )
    state = SimpleNamespace(
        entity_id="zone.home",
        name="Home",
        attributes={"latitude": 1, "longitude": 2, "radius": 100},
    )
    states = SimpleNamespace(
        async_all=lambda domain: [state] if domain == "zone" else [],
        async_entity_ids=lambda: {"light.desk", "switch.unregistered"},
        get=lambda entity_id: SimpleNamespace(attributes={"friendly_name": "Desk lamp"})
        if entity_id == "light.desk"
        else None,
    )
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_get_entry=lambda entry_id: SimpleNamespace(domain="demo_integration")
            if entry_id == "entry-1"
            else None
        ),
        data={websocket.DATA_EXPOSED_ENTITIES: object()},
        states=states,
    )
    monkeypatch.setattr(websocket.ar, "async_get", lambda _: areas_registry)
    monkeypatch.setattr(websocket.dr, "async_get", lambda _: devices_registry)
    monkeypatch.setattr(websocket.er, "async_get", lambda _: entities_registry)
    monkeypatch.setattr(websocket.cr, "async_get", lambda _: category_registry)
    monkeypatch.setattr(websocket.lr, "async_get", lambda _: label_registry)
    monkeypatch.setattr(websocket, "KNOWN_ASSISTANTS", ("conversation",))
    monkeypatch.setattr(
        websocket,
        "async_should_expose",
        lambda _, __, entity_id: entity_id == "light.desk",
    )

    snapshot = websocket._snapshot(hass)

    assert snapshot["areas"][0]["device_details"] == [
        {
            "id": "device-1",
            "name": "Desk Lamp",
            "integration": "demo_integration",
            "integration_name": "Demo Integration",
            "entity_ids": ["light.desk"],
        }
    ]
    assert snapshot["devices_without_area"][0]["name"] == "Virtual Device"
    assert snapshot["entities"][1]["name"] == "Outside sensor"
    assert snapshot["zones"] == [
        {
            "id": "home",
            "name": "Home",
            "latitude": 1,
            "longitude": 2,
            "radius": 100,
            "passive": False,
            "icon": None,
        }
    ]
    assert snapshot["exposed"] == [
        {
            "entity_id": "light.desk",
            "name": "Desk light",
            "aliases": ["Desk"],
            "assistants": ["conversation"],
        }
    ]
    assert snapshot["categories"]["automation"][0]["entities"] == ["light.desk"]
    assert snapshot["labels"][0]["name"] == "Important"
    assert websocket._device_integration(SimpleNamespace(), unassigned_device)[
        "integration"
    ] == "unknown"
