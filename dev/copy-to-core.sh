#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/custom_components/ha_organizer"
TARGET_DIR="/home/alves-dev/projects/others/core/config/custom_components/ha_organizer"
STOP_SCRIPT="$ROOT_DIR/dev/stop-ha.sh"
START_SCRIPT="$ROOT_DIR/dev/start-ha.sh"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Integration source not found: $SOURCE_DIR" >&2
  exit 1
fi

# Do not replace files while Home Assistant can load them.
"$STOP_SCRIPT"

sudo mkdir -p "$TARGET_DIR"
sudo find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
sudo cp -a "$SOURCE_DIR"/. "$TARGET_DIR"/

BUILD_ID="$(date '+%Y%m%d%H%M%S')"
BUILD_TIME="$(date '+%Y-%m-%d %H:%M:%S %Z')"
sudo sed -i "s|__HA_ORGANIZER_BUILD_TIME__|$BUILD_TIME|g" "$TARGET_DIR/frontend/ha-organizer.js"
sudo sed -i "s|v=release|v=$BUILD_ID|g" "$TARGET_DIR/panel.py"

echo "Copied ha_organizer to $TARGET_DIR at $BUILD_TIME"
"$START_SCRIPT"
