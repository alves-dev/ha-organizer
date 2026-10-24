# Changelog

All notable changes to HA Organizer are documented in this file.

## [2026.10.2] - 2026-10-24

### Fixed

- Review actions now update the cached audit result and Repairs without
  triggering a full Home Assistant inventory reanalysis.
- Module navigation now loads cached results, while the explicit refresh action
  remains the full analysis boundary.

## [2026.10.1] - 2026-10-22

### Fixed

- Fixed navigation sidebar overflow on desktop browsers and the iOS companion
  app.
- Fixed frontend localization from rewriting dynamic Home Assistant label names
  and descriptions, such as changing “Simon” to “Yeson”.
- Hid the read-only version text from the mobile navigation rail.
- Updated the Organizer panel to serve the current blue branding icon instead
  of the legacy purple asset.

### Changed

- Moved the desktop sidebar re-open control below the brand icon and added a
  mobile Home Assistant navigation button that does not rely on edge swipes.

## [2026.10.0] - 2026-10-22

### Fixed

- Areas now resolve Home Assistant `floor_id` values through the floor registry,
  so areas assigned to a floor no longer appear as “No floor”.
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

### Changed

- Updated the installation guidance to reflect that HA Organizer is now part
  of the official HACS default catalog, including direct HACS installation.

## [2026.8.0] - 2026-08-25

### Added

- Initial beta release of the HA Organizer custom integration.
- Read-only Organizer panel with Overview, Categories, Areas, Zones, Labels,
  Entity IDs, and Exposed & Aliases modules.
- Configurable audit policies for categories, zones, and Entity IDs.
- Deterministic findings with separate compliance and review statuses.
- Fingerprint-based stale review detection.
- Persistent Organizer settings and review decisions.
- Native Home Assistant links for areas, zones, labels, and exposed entities.
- HACS, Hassfest, test, and release workflow definitions.

### Changed

- Improved the Areas inventory with dedicated area and unassigned-device lists,
  expandable device details, icons, and native Home Assistant shortcuts.
- Improved Zones with a tabular inventory, icon and geometry details, and
  overlapping-zone detection.
- Improved Labels with visual icons, technical icon names, and color swatches.
- Expanded Categories to include Scenes, with one policy for requiring equal
  names and icons across Automation, Script, and Scene; scope-specific icon
  values are now shown directly in the audit table.
- Added native shortcuts for the Automation, Scene, and Script dashboards from
  Categories.
- Reworked Exposed & Aliases as a list, highlighted aliases, and added exposed
  entity and alias totals.
- Native Home Assistant shortcuts now open in a separate browser tab.
- Made the Organizer top bar more compact.
