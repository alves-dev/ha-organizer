# Changelog

## 2026-10-22

- Updated the Organizer panel icon endpoint to serve the current blue branding
  asset and bumped the frontend cache-busting version.

- Fixed the panel navigation sidebar overflow: the collapse control now stays
  inside the sidebar and navigation labels cannot widen it, preventing
  horizontal scrolling in desktop browsers and the iOS companion app.
- Panel cache-busting now uses the fixed integration version instead of
  performing synchronous filesystem metadata access during setup.
- Confirmed `alves-dev/ha-organizer` in the official HACS default integration
  catalog and updated the README installation guidance and HACS badge.

## [2026.10.1] - 2026-10-22

### Fixed

- Fixed navigation sidebar overflow on desktop browsers and the iOS companion
  app.
- Fixed frontend localization from rewriting dynamic Home Assistant label names
  and descriptions, such as changing “Simon” to “Yeson”.
- Hid the read-only version text from the mobile navigation rail.

### Changed

- Moved the desktop sidebar re-open control below the brand icon and added a
  mobile Home Assistant navigation button that does not rely on edge swipes.

## [2026.10.0] - 2026-10-22

### Fixed

- Area inventory now resolves Home Assistant `floor_id` values through the floor
  registry, so assigned areas display their floor name instead of “No floor”.
- Completed the light and dark branding asset set, including valid `@2x`
  variants and the Home Assistant-oriented blue palette.
- Added a visible beta notice to the Entity IDs and Exposed & Aliases modules
  to signal that these areas may change.
- Added the same beta marker to both modules in the sidebar navigation.
- Added the beta marker to the corresponding Entity IDs and Exposed & Aliases
  sections in Settings.
- Improved contrast for percentage values in Overview progress bars when using
  a dark Home Assistant theme.

### Added

- Added optional, per-module Home Assistant Repairs for non-compliant or
  attention items in Categories, Areas, Zones, and Labels.
- Repairs now use the integration translations and show the module/item in the
  title, findings and a direct link to HA Organizer. Areas create one Repair
  per actual area; unassigned-device findings remain in the Areas audit.
- Added a separate Areas setting for Repairs of pending devices without an
  area; ignored devices are excluded.
- Standardized the generated unassigned-device finding text in English so its
  Repair title remains localized consistently with the rest of the HA UI.
- Refactored zone auditing and Home Assistant snapshot assembly to comply with
  Ruff complexity limits without changing their output.
- Reviewed or ignored Zone and Label items now show only the Reopen action;
  Ignore is no longer offered for them.
- The Areas “Start with uppercase” policy now checks only the first alphabetic
  character, so compound names such as “Quarto Casal” remain valid.
- Settings now saves and restores every visible policy field in one update,
  including the Areas name-capitalization policy and module-specific
  normalization settings.

### Changed

- Progress by module now follows the same order as the Recommended organization
  flow: Areas, Zones, Labels, Categories, Entity IDs, and Exposed & Aliases.
- Zones now support an administrator-configured minimum name length and the
  same name-capitalization options as Areas.
- Recommended organization-flow steps now show a subtle completion check when
  all auditable items in that module have been reviewed or ignored.
- Area device lists are grouped by Home Assistant integration while retaining
  the compact device-row presentation. Integration groups use a readable
  integration-domain name and can select all unassigned devices in that group.
- Ignored unassigned devices now appear in a separate section with explicit
  status text and an action to restore an item to the pending review queue.
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
