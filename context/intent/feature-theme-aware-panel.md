# Feature: Theme-Aware Panel

## What

The HA Organizer panel follows the active Home Assistant theme for its primary
surfaces, typography, borders, interactive controls, and emphasis colors.

## Why

Administrators expect an embedded Home Assistant panel to feel visually
consistent with the interface they have chosen, including custom and dark
themes. A fixed Organizer palette can clash with that interface and reduce
readability.

## Acceptance Criteria

- [ ] The panel inherits the active Home Assistant theme without a separate
  Organizer color setting.
- [ ] Primary surfaces, text, borders, and main actions use the applicable
  Home Assistant theme colors.
- [ ] Compliance, attention, and error indicators remain distinguishable and
  readable with fallbacks when a theme omits optional semantic colors.
- [ ] Theme changes are reflected when Home Assistant rerenders the panel.

## Related

- [Project Intent](project-intent.md)
- [Decision: Theme Token Inheritance](../decisions/006-theme-token-inheritance.md)
- [Decision: Tech Stack](../decisions/001-tech-stack.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Approved for implementation
