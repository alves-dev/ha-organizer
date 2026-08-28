# Decision: Tech Stack

## Context

HA Organizer must run inside a Home Assistant installation, expose an administrator panel, and retain its own audit configuration and review progress.

## Decision

Use a Python Home Assistant custom integration targeting Home Assistant `2026.8.0`, with a native browser web component for the panel. Manage the development environment with `uv`; use pytest-family tools and Ruff for the configured quality workflow.

## Rationale

The manifest, pinned runtime dependency, integration lifecycle modules, custom-panel registration, JavaScript component, and project configuration all establish this stack. It aligns the product with the Home Assistant extension model and local administrator experience.

## Alternatives Considered

Alternatives are not documented in the existing codebase. A standalone application or a Home Assistant core contribution would not match the implemented custom-integration packaging and panel lifecycle.

## Outcomes

Outcomes to be documented as project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Registry-based Home Assistant Integration](005-registry-based-home-assistant-integration.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
