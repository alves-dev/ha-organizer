# Decision: Deterministic Audit and Review Model

## Context

The product must distinguish automatically calculated audit results from an administrator's progress, preserve review decisions, and require re-review only after meaningful data changes.

## Decision

Use a deterministic, pure audit engine that produces canonical findings, a calculated compliance status, and a stable fingerprint per audit item. Store human review status separately and mark it stale when its stored fingerprint differs from a subsequent scan.

## Rationale

The engine is separated from Home Assistant I/O, calculates findings from snapshots, and canonicalizes data before hashing. This produces repeatable audits while allowing a review to remain valid until relevant source data changes.

## Alternatives Considered

The existing codebase does not document alternatives. A single combined status would lose the distinction between a policy result and a human decision; volatile scan timestamps or source ordering would make reviews stale unnecessarily.

## Outcomes

Outcomes to be documented as project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Overview and Review Progress](../intent/feature-overview-and-review-progress.md)
- [Feature: Category Consistency](../intent/feature-category-consistency.md)
- [Feature: Zone Inventory](../intent/feature-zone-inventory.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
