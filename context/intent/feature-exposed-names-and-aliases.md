# Feature: Exposed Names and Aliases

## What

Audits resources made available to voice assistants, including their effective names and aliases, and identifies collisions or records that need review.

## Why

Conflicting or unclear spoken names can make voice control unreliable. Administrators need visibility into possible ambiguities before they affect household use.

## Acceptance Criteria

- [x] Lists resources currently exposed to supported voice assistants.
- [x] Shows associated names and aliases.
- [x] Identifies collisions and other reviewable conditions.
- [x] Provides a direct route to Home Assistant exposure management.

## Related

- [Project Intent](project-intent.md)
- [Decision: Registry-based Home Assistant Integration](../decisions/005-registry-based-home-assistant-integration.md)
- [Decision: Read-only Native Resource Navigation](../decisions/004-read-only-native-resource-navigation.md)
- [Pattern: Registry Snapshot Boundary](../knowledge/patterns/registry-snapshot-boundary.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active (already implemented)
