# Changelog

All notable changes to HA Organizer are documented in this file.

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
