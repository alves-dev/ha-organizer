# Changelog

## [Unreleased]

### Fixed

- Settings now saves and restores every visible policy field in one update,
  including the Areas name-capitalization policy and module-specific
  normalization settings.

### Changed

- Areas now support recorded review after inspecting their devices. Devices
  without an area can be searched by name, device ID, or entity ID and ignored
  in an administrator-only batch action; Overview shows this review progress.
- Added concise in-context descriptions to every Settings control so
  administrators can understand the audit effect before saving a policy.
- Ordered Settings modules to match the panel workflow and standardized module
  icons on Home Assistant's monochrome Material Design icon set.
- The Organizer panel now inherits Home Assistant theme tokens for its main
  surfaces, typography, borders, and primary actions, with accessible fallbacks
  and semantic status colors.
- Moved the local integration copy script to `dev/copy-to-core.sh` and documented the stop, update, start, and MCP exploratory-test workflow for agents.

## [Current State] - Context Mesh Added

### Existing Features (documented)

- Overview and review progress - consolidated audit status and continuation of reviews.
- Category consistency - audits selected category scopes.
- Area, zone, and label inventories - identify organization issues in native resources.
- Entity ID policy audit - checks identifiers against an administrator policy.
- Exposed names and aliases - identifies potential voice-control collisions.

### Tech Stack (documented)

- Python 3.14 Home Assistant custom integration targeting Home Assistant 2026.8.0.
- Native custom panel web component with Home Assistant WebSocket commands.
- `uv` environment management, pytest tooling, Ruff, and SonarQube configuration.

### Patterns Identified

- Canonical findings and fingerprint-based stale reviews.
- Registry snapshot boundary around a pure audit engine.
- Administrator-protected WebSocket commands for Organizer-owned state.

*Context Mesh added: 2026-08-28*
*This changelog documents the state when Context Mesh was added.*
*Future changes will be tracked below.*
