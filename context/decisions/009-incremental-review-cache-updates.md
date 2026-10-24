# Decision: Incremental Review Cache Updates

## Context

Recording a review changes Organizer-owned state, but does not change the
Home Assistant registries that feed the audit. Rebuilding the complete
registry snapshot after every review makes reviewing many areas unnecessarily
slow.

## Decision

Persist review changes and reapply them to the existing `last_scan` result.
Synchronize Repairs from that updated result without rebuilding the Home
Assistant snapshot. The explicit refresh action remains responsible for
detecting changes in native Home Assistant resources.

## Rationale

This preserves the deterministic fingerprint and stale-review model while
keeping review actions fast. It also keeps Overview, module results, and
Repairs consistent immediately after an individual or batch review.

## Alternatives Considered

Keeping the frontend-only state would make the Overview and Repairs stale.
Running a full scan after every review preserves freshness but recreates the
performance problem reported in issue #11.

## Related

- [Feature: Area Review Workflow](../intent/feature-area-review-workflow.md)
- [Decision: Deterministic Audit and Review Model](002-deterministic-audit-and-review-model.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)

## Status

- **Created**: 2026-10-24 (Phase: Decision)
- **Status**: Accepted
