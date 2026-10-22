# Feature: Area Review Workflow

## What

Lets administrators confirm that an area's assigned devices have been checked,
and dismiss devices without an area when they are intentionally virtual or do
not require an area assignment.

## Why

An inventory is only useful when its review can be recorded. Administrators
need to distinguish inspected areas and intentionally unassigned virtual
devices from the work that still requires attention.

## Acceptance Criteria

- [x] An administrator can mark an area as reviewed after inspecting its
  device list, and can reopen that review.
- [x] Devices without an area show their technical device ID and associated
  entity IDs.
- [x] The unassigned-device list can be searched by device name, device ID, or
  associated entity ID.
- [x] An administrator can select visible unassigned devices and ignore them
  in one action.
- [x] Area-specific review and ignored-device progress is visible on Overview.
- [x] Review decisions become outdated when their relevant inventory changes.

## Related

- [Project Intent](project-intent.md)
- [Feature: Area Inventory](feature-area-inventory.md)
- [Feature: Overview and Review Progress](feature-overview-and-review-progress.md)
- [Decision: Batch Review Actions](../decisions/007-batch-review-actions.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)
- [Pattern: Admin WebSocket Command](../knowledge/patterns/admin-websocket-command.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Implemented
