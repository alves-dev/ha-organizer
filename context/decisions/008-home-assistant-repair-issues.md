# Decision: Optional Home Assistant Repair Issues

## Context

Administrators may want Home Assistant to surface Organizer findings while
working through a large installation gradually. The Organizer must remain
read-only and must not silently create a large number of native-resource
changes or actions.

## Decision

Create one informational Home Assistant issue for each non-compliant or
attention item in Categories, Areas, Zones, and Labels when that module's
`create_repairs` setting is enabled. Repairs are persistent, non-fixable issue
registry entries. Their translated title and description include the module,
item, status, findings, rule identifiers, and resource references.

For Areas, the Repair unit is an actual registered area. The Areas audit may
also report devices without an area, but those remain in the audit view rather
than producing additional area Repairs.

Devices without an area have a separate opt-in setting. When enabled, it
creates one non-fixable Repair per device whose review status is `pending`.
Ignored devices never create a Repair, and any existing issue is removed after
the device is ignored.

Synchronize issues after scans and configuration changes. Delete issues when
the item becomes compliant, disappears from the scan, or the module setting is
disabled. The setting is disabled by default for every module.

## Rationale

The Home Assistant issue registry provides the native Repairs surface while
preserving the integration's read-only boundary. Stable issue IDs derived from
canonical item keys prevent duplicates, and scan-time cleanup prevents stale
notifications from accumulating as the installation is organized.

## Alternatives Considered

Adding fix flows would imply that Organizer edits native areas, zones, labels,
or categories, which conflicts with the read-only product boundary. Creating a
single aggregate issue per module would make it harder to work through items
individually.

## Related

- [Feature: Area Inventory](../intent/feature-area-inventory.md)
- [Feature: Zone Inventory](../intent/feature-zone-inventory.md)
- [Feature: Label Inventory](../intent/feature-label-inventory.md)
- [Feature: Category Consistency](../intent/feature-category-consistency.md)
- [Decision: Deterministic Audit and Review Model](002-deterministic-audit-and-review-model.md)

## Status

- **Created**: 2026-10-22 (Phase: Build)
- **Status**: Accepted
