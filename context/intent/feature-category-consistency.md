# Feature: Category Consistency

## What

Audits categories used by automations, scripts, and scenes for consistency, missing presence, name variations, and policy violations.

## Why

Consistent categories make Home Assistant automations, scripts, and scenes easier to browse, understand, and maintain as an installation grows.

## Acceptance Criteria

- [x] Lets administrators choose the category scopes to audit.
- [x] Identifies inconsistent or missing category presence across selected scopes.
- [x] Highlights names and icons that need attention according to the selected policy.
- [x] Lets administrators record their review of an audit item.

## Related

- [Project Intent](project-intent.md)
- [Decision: Module-specific Audit Policies](../decisions/003-module-specific-audit-policies.md)
- [Pattern: Canonical Findings and Stale Reviews](../knowledge/patterns/canonical-findings-and-stale-reviews.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active (already implemented)
