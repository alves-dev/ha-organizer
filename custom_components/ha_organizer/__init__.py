"""HA Organizer: a read-only audit of Home Assistant organisation."""

from __future__ import annotations

from .const import DOMAIN

try:  # Keep the deterministic engine importable in standalone test tooling.
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .panel import async_register_panel
    from .websocket import async_register_websocket_commands
except ImportError:  # Home Assistant supplies these at runtime.
    ConfigEntry = object
    HomeAssistant = object
    async_register_websocket_commands = None
    async_register_panel = None


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    if async_register_websocket_commands:
        async_register_websocket_commands(hass)
        await async_register_panel(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data | dict(entry.options)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
