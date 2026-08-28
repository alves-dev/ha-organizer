# Decision: Module-specific Audit Policies

## Context

Each audit area has different meaningful rules: categories need scope comparison, zones need geometry checks, labels need metadata checks, and entity IDs need an installation-specific naming policy.

## Decision

Keep policy settings scoped to the relevant audit module, with module enablement and defaults retained by the Organizer. Permit administrators to configure the entity-ID policy used for auditing rather than relying on a non-existent global Home Assistant policy.

## Rationale

The configuration structure and policy UI contain separate settings for categories, zones, labels, and entity IDs. This avoids applying an artificial one-size-fits-all normalization or validation policy to unrelated resources.

## Alternatives Considered

A shared global normalization section exists in the current default configuration and is also recognized by validation, but the product instructions state that module-specific policies are the intended beta direction. A globally enforced entity-ID policy is not available from Home Assistant and is therefore not used.

## Outcomes

The Settings panel persists each visible module-specific policy in one complete
configuration update. Area metadata requirements, name capitalization, and
normalization rules are retained independently from other modules.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Category Consistency](../intent/feature-category-consistency.md)
- [Feature: Zone Inventory](../intent/feature-zone-inventory.md)
- [Feature: Label Inventory](../intent/feature-label-inventory.md)
- [Feature: Entity ID Policy Audit](../intent/feature-entity-id-policy-audit.md)

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation; rationale partly inferred
