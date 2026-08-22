from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.helpers.storage import Store

from .const import DEFAULT_CONFIG, DOMAIN, VERSION


class OrganizerStore:
    def __init__(self, hass):
        self._store = Store(hass, VERSION, f"{DOMAIN}.data", private=True)
        self.data = None

    async def async_load(self):
        self.data = await self._store.async_load() or {
            "schema_version": VERSION,
            "config": DEFAULT_CONFIG.copy(),
            "reviews": {},
            "last_scan": None,
        }
        self.data.setdefault("reviews", {})
        self.data.setdefault("config", DEFAULT_CONFIG.copy())
        return self.data

    async def async_save(self):
        await self._store.async_save(self.data)

    async def set_review(self, item_key, status, current_fingerprint, note=None):
        if status not in ("reviewed", "ignored", "pending"):
            raise ValueError("invalid review status")
        if status == "pending":
            self.data["reviews"].pop(item_key, None)
        else:
            self.data["reviews"][item_key] = {
                "review_status": status,
                "reviewed_fingerprint": current_fingerprint,
                "reviewed_at": datetime.now(UTC).isoformat(),
                "note": note,
            }
        await self.async_save()
