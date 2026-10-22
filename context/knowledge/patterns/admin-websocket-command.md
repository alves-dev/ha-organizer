# Pattern: Admin WebSocket Command

## Description

Expose panel operations as individually registered Home Assistant WebSocket commands that enforce administrator access and validate input before changing Organizer-owned state.

## When to Use

Use this when the custom panel needs a new request for scanning, configuration, or review state. Do not use it to mutate native Home Assistant resources.

## Pattern

Decorate the handler with a command schema and asynchronous response support, reject non-administrators first, validate user-provided data, use the Organizer store, and explicitly register the command.

## Example

```python
@websocket_api.websocket_command({"type": "ha_organizer/config/get"})
@websocket_api.async_response
async def config_get(hass, connection, msg):
    if not _admin(connection):
        return connection.send_error(msg["id"], "not_allowed", ADMIN_REQUIRED)
    _, data = await _store(hass)
    connection.send_result(msg["id"], data.get("config", DEFAULT_CONFIG))

websocket_api.async_register_command(hass, config_get)
```

## Files Using This Pattern

- [websocket.py](../../../custom_components/ha_organizer/websocket.py) - defines configuration, scan, review, reset, and overview commands.
- [ha-organizer.js](../../../custom_components/ha_organizer/frontend/ha-organizer.js) - calls commands from the panel with `callWS`.

## Related

- [Decision: Tech Stack](../../decisions/001-tech-stack.md)
- [Decision: Read-only Native Resource Navigation](../../decisions/004-read-only-native-resource-navigation.md)
- [Feature: Overview and Review Progress](../../intent/feature-overview-and-review-progress.md)

## Status

- **Created**: 2026-08-28
- **Status**: Active
