# Decision: Theme Token Inheritance

## Context

The custom panel currently owns a fixed visual palette. Home Assistant exposes
CSS custom properties for the active theme to its panel content, including
surface, text, divider, and primary-action colors.

## Decision

Use Home Assistant CSS theme variables as the Organizer's semantic visual
tokens. Provide CSS fallbacks only for compatibility with incomplete themes.
Keep the panel's status colors semantic and distinct, using Home Assistant
semantic variables when available.

## Rationale

CSS custom properties inherit into the native panel web component, so this
approach applies to built-in, dark, and user-defined themes without storing or
managing a second theme preference. A semantic token layer also keeps future
visual changes localized.

## Alternatives Considered

- Maintain an Organizer-specific light and dark palette: rejected because it
  can conflict with user themes and duplicates theme selection.
- Add a panel color configuration: rejected because it adds a preference that
  Home Assistant themes already supply.

## Outcomes

The frontend consumes theme tokens for its main visual surfaces and preserves
readable fallback values for absent optional tokens.

## Related

- [Feature: Theme-Aware Panel](../intent/feature-theme-aware-panel.md)
- [Decision: Tech Stack](001-tech-stack.md)

## Status

- **Created**: 2026-08-28 (Phase: Decision)
- **Status**: Accepted
