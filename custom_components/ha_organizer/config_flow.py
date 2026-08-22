from __future__ import annotations

from homeassistant import config_entries
import voluptuous as vol

from .const import DEFAULT_CONFIG, DOMAIN, NAME


class HaOrganizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title=NAME, data=DEFAULT_CONFIG)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
