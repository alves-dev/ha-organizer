# Decision: Registry-based Home Assistant Integration

## Context

The audit needs a consistent view of areas, devices, entities, categories, labels, zones, and voice-assistant exposure without changing those resources.

## Decision

Build a Home Assistant snapshot from native registries and state data, then pass that snapshot to the audit engine. Resolve voice-assistant exposure through Home Assistant's exposure facilities and registry options.

## Rationale

The snapshot code gathers native records at scan time and derives audit-friendly values, while the core engine deliberately has no Home Assistant I/O. This separates platform access from audit logic and accounts for both exposure storage paths.

## Alternatives Considered

The existing code does not document alternatives. Direct mutations or tying audit rules to live registry objects would conflict with the read-only boundary and deterministic engine design.

## Outcomes

Outcomes to be documented as project evolves.

## Related

- [Decision: Tech Stack](001-tech-stack.md)
- [Feature: Area Inventory](../intent/feature-area-inventory.md)
- [Feature: Label Inventory](../intent/feature-label-inventory.md)
- [Feature: Exposed Names and Aliases](../intent/feature-exposed-names-and-aliases.md)
- [Pattern: Registry Snapshot Boundary](../knowledge/patterns/registry-snapshot-boundary.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
