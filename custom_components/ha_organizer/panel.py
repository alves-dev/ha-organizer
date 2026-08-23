from __future__ import annotations

from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant


async def async_register_panel(hass: HomeAssistant):
    path = str(Path(__file__).parent / "frontend" / "ha-organizer.js")
    icon_path = str(Path(__file__).parent / "icon.png")
    await hass.http.async_register_static_paths(
        [
            # Change the resource URL whenever the installed file changes so
            # browsers do not keep stale frontend code after local copies.
            StaticPathConfig("/ha_organizer/ha-organizer.js", path, False),
            StaticPathConfig("/ha_organizer/icon.png", icon_path, True),
        ]
    )
    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path="ha-organizer",
        webcomponent_name="ha-organizer",
        sidebar_title="HA Organizer",
        sidebar_icon="mdi:format-list-checks",
        module_url=f"/ha_organizer/ha-organizer.js?v={Path(path).stat().st_mtime_ns}",
        embed_iframe=False,
        require_admin=True,
    )
