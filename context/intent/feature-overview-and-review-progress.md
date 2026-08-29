# Feature: Overview and Review Progress

## What

Provides a consolidated view of the Organizer audit, including audit totals, compliance results, review progress, stale reviews, and progress by audit area. It also presents a recommended order for organizing an installation.

## Why

Administrators need to understand the scale and state of an organization review at a glance, prioritize follow-up work, and resume a review across multiple sessions.

## Acceptance Criteria

- [x] Shows a combined summary for enabled audit areas.
- [x] Keeps technical compliance distinct from human review progress.
- [x] Identifies items whose previous review is no longer current.
- [x] Shows progress for each enabled audit area.
- [x] Orders progress by audit area using the recommended organization flow.

## Related

- [Project Intent](project-intent.md)
- [Decision: Deterministic Audit and Review Model](../decisions/002-deterministic-audit-and-review-model.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active (already implemented)
