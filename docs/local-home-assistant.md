# Shared local Home Assistant test instance

<!-- local-home-assistant-reference-version: 2026.10.27.1 -->

Reference version: `2026.10.27.1`

Last verified: `2026-10-27` through the Home Assistant UI.

All integrations use the same containerized Home Assistant development
instance. Do not start a second Home Assistant process for an integration.

- Container: `hass-dev-homeassistant`
- Image: `homeassistant/home-assistant:dev`
- Host configuration: `/home/alves-dev/projects/others/infra/local-dev/hass-dev/data`
- Container configuration: `/config`
- Web interface: `http://localhost:9123`
- Administrator username: `homer`
- Administrator password: `HomerSimpson123!`

The host configuration is mounted into the container and contains the shared
Home Assistant state, configuration, and `custom_components/` directory. Use
`dev/start-ha.sh` and `dev/stop-ha.sh` to control the container. Use
`dev/deploy-to-ha.sh` to stop the instance, replace this integration in the
mounted configuration, and start it again.

## Test inventory

This inventory is a snapshot of the shared development instance. Use the Home
Assistant UI as the source of truth if the instance changes, then increment the
reference version and update this file before synchronizing integration
repositories.

### People

- Bart
- Demo User
- Homer
- Lisa
- Maggie
- Marge

### Users

- `homer` — Homer, Administrators
- `demo` — Demo User, Owner
- Two system `Home Assistant Content` users, Read-only users

### Floors and areas

- Upper Floor
  - Homer and Marge's Bedroom (`homer_and_marge_s_bedroom`)
  - Bart's Room (`bart_s_room`)
  - Lisa's Room (`lisa_s_room`)
  - Maggie's Room (`maggie_s_room`)
  - Bathroom (`bathroom`)
- Ground Floor
  - Living Room (`living_room`)
  - Kitchen (`kitchen`)
  - Dining Room (`dining_room`)
  - Garage (`garage`)
  - Backyard (`backyard`)

### Labels and zones

- Labels: none currently configured.
- Zones:
  - Demo Home
  - Downtown Uberlandia
  - Tech Campus
  - Uberlandia

### Configured integrations

- Backup — 1 service
- Google Translate text-to-speech — 1 service
- HA Organizer — 1 entry
- Integration Tracker — 1 entry
- Radio Browser — 1 entry
- Shopping list — 1 entity
- Sun — 1 service

### Devices

- Backup — Home Assistant Backup
- Google Translate en com — Google Translate TTS
- HA Organizer — `alves-dev` / `integration`
- Sun

### Entities useful for tests

- Backup: Automatic backup (event), Backup Manager state (`idle`), Last
  attempted automatic backup (event), Last successful automatic backup
  (event), Last successful automatic backup size, and Next scheduled automatic
  backup.
- Google Translate: Google Translate en com.
- HA Organizer: HA Organizer (`Up-to-date`).
- Sun: Next dawn, Next dusk, Next midnight, Next noon, Next rising, and Next
  setting.
- Person entities: Bart, Demo User, Homer, Lisa, Maggie, and Marge.
- Zone entities: Demo Home (`0`) and Downtown Uberlandia (`0`).
- Conversation entity: Home Assistant.
- Shopping list entity: Shopping list (`0`).

The UI reported 27 entities in total at verification time. The list above
contains the names and states exposed in the visible entity inventory. Query
Home Assistant directly when a test needs exact entity IDs or the complete
current registry.

### Automations, scenes, scripts, helpers, and lists

- Automations: none currently configured.
- Scenes: none currently configured.
- Scripts: none currently configured.
- Helpers: none currently configured.
- To-do lists: `Shopping list`, currently empty.

### Dashboards

- Overview
- Lights
- Security
- Climate
- Energy
- Maintenance
- Map

These credentials are for the local development instance only. Never reuse
them in production, documentation for end users, or automated release
workflows.
