# Pattern: Registry Snapshot Boundary

## Description

Collect Home Assistant data at the integration boundary into plain dictionaries, then give those dictionaries to a pure audit engine.

## When to Use

Use this when an audit module needs platform data but its validation logic should stay deterministic, testable, and independent of Home Assistant runtime objects.

## Pattern

Read the necessary native registry and state records once per scan. Resolve relationships at the boundary, reduce objects to the fields relevant to auditing, and return a serializable snapshot.

## Example

```python
areas_reg = ar.async_get(hass)
devices_reg = dr.async_get(hass)
entities_reg = er.async_get(hass)

entities = []
for entity in entities_reg.entities.values():
    device = devices_reg.async_get(entity.device_id) if entity.device_id else None
    area = _entity_area(areas_reg, device, entity)
    entities.append(
        {
            "entity_id": entity.entity_id,
            "name": entity.name or entity.original_name,
            "area_id": area.id if area else None,
            "device_id": entity.device_id,
            "platform": entity.platform,
        }
    )

return {"areas": areas, "entities": entities, "zones": zones, "labels": labels}
```

## Files Using This Pattern

- [websocket.py](../../../custom_components/ha_organizer/websocket.py) - builds the runtime snapshot from registries and states.
- [core.py](../../../custom_components/ha_organizer/core.py) - consumes plain snapshots without Home Assistant I/O.
- [tests](../../../tests) - supplies plain snapshot fixtures to exercise audit behavior.

## Related

- [Decision: Registry-based Home Assistant Integration](../../decisions/005-registry-based-home-assistant-integration.md)
- [Feature: Exposed Names and Aliases](../../intent/feature-exposed-names-and-aliases.md)

## Status

- **Created**: 2026-08-28
- **Status**: Active
