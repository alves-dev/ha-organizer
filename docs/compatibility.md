# Compatibility Matrix

The table below lists the Home Assistant versions tested with each HA Organizer
version. A version not listed has not been validated by the project and may or
may not work.

| HA Organizer version | Home Assistant supported | Home Assistant not supported |
|----------------------|--------------------------|------------------------------|
| `2026.8.0` beta      | `2026.8.x`               | —                            |

## Validation scope

The supported combination is checked through:

- Home Assistant dependency resolution and Hassfest validation;
- HACS integration validation;
- automated Ruff and pytest checks;
- local integration testing against a Home Assistant `2026.8.0` checkout;
- SonarQube analysis, including the generated Python coverage report.

Compatibility outside the listed Home Assistant series is not guaranteed. When
the integration or Home Assistant version changes, update this table only after
the complete validation workflow has passed.
