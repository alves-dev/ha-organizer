#!/bin/sh
# Deploy this integration to the containerized Home Assistant test instance.

set -eu

readonly INTEGRATION_DOMAIN="ha_organizer"
readonly ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
# Source component: custom_components/ha_organizer
readonly SOURCE_DIR="$ROOT_DIR/custom_components/ha_organizer"
readonly HA_CONFIG_DIR="/home/alves-dev/projects/others/infra/local-dev/hass-dev/data"
readonly TARGET_DIR="$HA_CONFIG_DIR/custom_components/$INTEGRATION_DOMAIN"
readonly CONTAINER_NAME="hass-dev-homeassistant"
readonly CONTAINER_IMAGE="homeassistant/home-assistant:dev"
readonly STOP_SCRIPT="$ROOT_DIR/dev/stop-ha.sh"
readonly START_SCRIPT="$ROOT_DIR/dev/start-ha.sh"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Integration source not found: $SOURCE_DIR" >&2
  exit 1
fi

if [ ! -d "$HA_CONFIG_DIR" ]; then
  echo "Home Assistant configuration directory was not found: $HA_CONFIG_DIR" >&2
  exit 1
fi

sh "$STOP_SCRIPT"

restart_after_failure() {
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "Deployment failed; restarting Home Assistant container." >&2
    sh "$START_SCRIPT" || true
  fi
  exit "$status"
}

trap restart_after_failure EXIT

readonly STAGING_PATH="/config/custom_components/.${INTEGRATION_DOMAIN}.staging"

docker run --rm --entrypoint /bin/sh -v "$HA_CONFIG_DIR:/config" "$CONTAINER_IMAGE" \
  -c "mkdir -p /config/custom_components && rm -rf /config/custom_components/$INTEGRATION_DOMAIN '$STAGING_PATH'"
docker cp "$SOURCE_DIR" "$CONTAINER_NAME:$STAGING_PATH"
docker run --rm --entrypoint /bin/sh -v "$HA_CONFIG_DIR:/config" "$CONTAINER_IMAGE" \
  -c "mv '$STAGING_PATH' /config/custom_components/$INTEGRATION_DOMAIN"

echo "Copied $INTEGRATION_DOMAIN to $TARGET_DIR."
trap - EXIT
sh "$START_SCRIPT"
