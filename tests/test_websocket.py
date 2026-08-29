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
    await handlers["reviews_reset"](hass, connection, {"id": 8})
    await handlers["config_reset"](hass, connection, {"id": 9})
    await handlers["do_scan"](hass, connection, {"id": 10})
    await handlers["get_overview"](hass, connection, {"id": 11})
    assert any(error[1] == "invalid_status" for error in connection.errors)
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
