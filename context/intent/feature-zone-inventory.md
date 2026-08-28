# Feature: Zone Inventory

## What

Inventories configured geographic zones and flags potentially problematic names, metadata, and geometry.

## Why

Zones are often used in location-aware automations. A clear inventory helps administrators identify ambiguous, incomplete, or overlapping zone definitions before they cause confusion.

## Acceptance Criteria

- [x] Lists configured zones and their relevant details.
- [x] Highlights duplicate or overlapping geometry when those checks are enabled.
- [x] Applies the chosen zone policy to the inventory.
- [x] Provides a direct route to manage zones in Home Assistant.

## Related

- [Project Intent](project-intent.md)
- [Decision: Module-specific Audit Policies](../decisions/003-module-specific-audit-policies.md)
- [Decision: Read-only Native Resource Navigation](../decisions/004-read-only-native-resource-navigation.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active (already implemented)
