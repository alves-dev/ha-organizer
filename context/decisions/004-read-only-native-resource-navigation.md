# Decision: Read-only Native Resource Navigation

## Context

The integration audits organization issues but should not create, rename, or otherwise mutate native Home Assistant resources.

## Decision

Keep HA Organizer read-only for native data and direct administrators to native Home Assistant screens when they need to make changes. Render those links as normal links that open in a separate tab.

## Rationale

The product specification and panel behavior make auditing and manual correction separate workflows. This reduces the risk of unintended data changes while still making follow-up action straightforward.

## Alternatives Considered

Editing native resources through Organizer WebSocket commands is explicitly excluded by the implemented product boundary. Alternatives beyond this are not documented in the existing codebase.

## Outcomes

Outcomes to be documented as project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Area Inventory](../intent/feature-area-inventory.md)
- [Feature: Zone Inventory](../intent/feature-zone-inventory.md)
- [Feature: Entity ID Policy Audit](../intent/feature-entity-id-policy-audit.md)
- [Feature: Exposed Names and Aliases](../intent/feature-exposed-names-and-aliases.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
