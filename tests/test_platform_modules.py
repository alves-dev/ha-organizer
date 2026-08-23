from types import SimpleNamespace

import pytest

from custom_components.ha_organizer import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
    config_flow,
    panel,
    storage,
)
from custom_components.ha_organizer.const import DEFAULT_CONFIG, DOMAIN, VERSION


class FakeHass:
    def __init__(self):
        self.data = {}


@pytest.mark.asyncio
async def test_integration_setup_and_entry_lifecycle(monkeypatch):
    hass = FakeHass()
    registered = []

    def register_websocket(value):
        registered.append(value)

    monkeypatch.setattr(
        "custom_components.ha_organizer.async_register_websocket_commands",
        register_websocket,
    )

    async def register_panel(value):
        registered.append(value)

    monkeypatch.setattr(
        "custom_components.ha_organizer.async_register_panel", register_panel
    )
    entry = SimpleNamespace(entry_id="entry", data={"a": 1}, options={"b": 2})

    assert await async_setup(hass, {}) is True
    assert registered == [hass, hass]
    assert await async_setup_entry(hass, entry) is True
    assert hass.data[DOMAIN]["entry"] == {"a": 1, "b": 2}
    assert await async_unload_entry(hass, entry) is True
    assert "entry" not in hass.data[DOMAIN]


class FakeStore:
    loaded = None

    def __init__(self, hass, version, key, private):
        self.saved = []

    async def async_load(self):
        return self.loaded

    async def async_save(self, data):
        self.saved.append(data.copy())


@pytest.mark.asyncio
async def test_organizer_store_defaults_and_preserves_loaded_data(monkeypatch):
    monkeypatch.setattr(storage, "Store", FakeStore)
    FakeStore.loaded = None
    store = storage.OrganizerStore(FakeHass())
    data = await store.async_load()
    assert data["schema_version"] == VERSION
    assert data["config"] == DEFAULT_CONFIG
    assert data["reviews"] == {}

    FakeStore.loaded = {"schema_version": VERSION, "last_scan": "now"}
    loaded = storage.OrganizerStore(FakeHass())
    assert await loaded.async_load() == {
        "schema_version": VERSION,
        "last_scan": "now",
        "reviews": {},
        "config": DEFAULT_CONFIG,
    }


@pytest.mark.asyncio
async def test_organizer_store_reviews_and_save(monkeypatch):
    monkeypatch.setattr(storage, "Store", FakeStore)
    FakeStore.loaded = {"reviews": {}, "config": {}}
    organizer = storage.OrganizerStore(FakeHass())
    await organizer.async_load()
    await organizer.set_review("item", "reviewed", "fingerprint", "note")
    assert organizer.data["reviews"]["item"]["review_status"] == "reviewed"
    await organizer.set_review("item", "ignored", "new-fingerprint")
    assert organizer.data["reviews"]["item"]["review_status"] == "ignored"
    await organizer.set_review("item", "pending", "new-fingerprint")
    assert "item" not in organizer.data["reviews"]
    with pytest.raises(ValueError, match="invalid review status"):
        await organizer.set_review("item", "invalid", "fingerprint")
    assert organizer._store.saved


@pytest.mark.asyncio
async def test_config_flow_shows_form_and_creates_entry(monkeypatch):
    flow = config_flow.HaOrganizerConfigFlow()
    monkeypatch.setattr(flow, "_async_current_entries", lambda: [])
    shown = await flow.async_step_user()
    assert shown["type"] == "form"
    created = await flow.async_step_user({})
    assert created["type"] == "create_entry"
    assert created["data"] == DEFAULT_CONFIG


@pytest.mark.asyncio
async def test_config_flow_blocks_second_instance(monkeypatch):
    flow = config_flow.HaOrganizerConfigFlow()
    monkeypatch.setattr(flow, "_async_current_entries", lambda: [object()])
    aborted = await flow.async_step_user()
    assert aborted["type"] == "abort"
    assert aborted["reason"] == "single_instance_allowed"


@pytest.mark.asyncio
async def test_panel_registers_static_paths_and_sidebar(monkeypatch, tmp_path):
    static_paths = []

    class Http:
        async def async_register_static_paths(self, paths):
            static_paths.extend(paths)

    async def register_panel(**kwargs):
        register_panel.kwargs = kwargs

    monkeypatch.setattr(panel.panel_custom, "async_register_panel", register_panel)
    hass = SimpleNamespace(http=Http())
    await panel.async_register_panel(hass)
    assert [item.url_path for item in static_paths] == [
        "/ha_organizer/ha-organizer.js",
        "/ha_organizer/icon.png",
    ]
    assert register_panel.kwargs["frontend_url_path"] == "ha-organizer"
    assert register_panel.kwargs["require_admin"] is True
