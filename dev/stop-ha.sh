#!/bin/sh
# Stop the containerized Home Assistant instance used by start-ha.sh.

set -eu

readonly CONTAINER_NAME="hass-dev-homeassistant"

if ! docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  echo "Home Assistant container was not found: $CONTAINER_NAME"
  exit 0
fi

running="$(docker inspect --format '{{.State.Running}}' "$CONTAINER_NAME")"
if [ "$running" != "true" ]; then
  echo "Home Assistant container is already stopped: $CONTAINER_NAME"
  exit 0
fi

docker stop "$CONTAINER_NAME" >/dev/null
echo "Home Assistant container stopped: $CONTAINER_NAME"
