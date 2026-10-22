# Decision: Batch Review Actions

## Context

Administrators may have many intentionally virtual devices that do not need an
area. Applying an ignore decision one device at a time makes the audit workflow
needlessly slow.

## Decision

Represent every decision as an existing per-item Organizer review. Add an
administrator-only batch command that validates and stores a bounded list of
item-key and fingerprint pairs with one requested review status. It does not
mutate Home Assistant devices or entities.

## Rationale

This retains the existing deterministic fingerprint and stale-review model for
each device while making the common bulk-dismissal workflow efficient. The
Overview can use normal review aggregation without inventing a second status
system.

## Alternatives Considered

Persisting a separate virtual-device exclusion list would bypass fingerprints
and could hide a device after its meaningful identity changed. Changing device
area assignments through Organizer would violate its read-only boundary.

## Related

- [Feature: Area Review Workflow](../intent/feature-area-review-workflow.md)
- [Decision: Deterministic Audit and Review Model](002-deterministic-audit-and-review-model.md)
- [Pattern: Admin WebSocket Command](../knowledge/patterns/admin-websocket-command.md)

## Status

- **Created**: 2026-08-28 (Phase: Decision)
- **Status**: Accepted
