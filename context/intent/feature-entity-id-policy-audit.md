# Feature: Entity ID Policy Audit

## What

Compares entity identifiers with an administrator-defined naming policy and highlights identifiers that need review.

## Why

Predictable entity identifiers make templates, automations, and long-term maintenance less error-prone, while still allowing each installation to define its own naming convention.

## Acceptance Criteria

- [x] Audits entity identifiers against a configured policy.
- [x] Supports excluding selected domains from the audit.
- [x] Shows identifiers that do not meet the policy or appear to need attention.
- [x] Does not rename native identifiers.

## Related

- [Project Intent](project-intent.md)
- [Decision: Module-specific Audit Policies](../decisions/003-module-specific-audit-policies.md)
- [Decision: Read-only Native Resource Navigation](../decisions/004-read-only-native-resource-navigation.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active (already implemented)
