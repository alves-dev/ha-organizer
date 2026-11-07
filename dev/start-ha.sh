#!/bin/sh
# Start the containerized Home Assistant instance used by custom integrations.

set -eu

readonly CONTAINER_NAME="hass-dev-homeassistant"

if ! docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  echo "Home Assistant container was not found: $CONTAINER_NAME" >&2
  exit 1
fi

running="$(docker inspect --format '{{.State.Running}}' "$CONTAINER_NAME")"
if [ "$running" = "true" ]; then
  echo "Home Assistant container is already running: $CONTAINER_NAME"
  exit 0
fi

docker start "$CONTAINER_NAME" >/dev/null
echo "Home Assistant container started: $CONTAINER_NAME"
