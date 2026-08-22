#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/custom_components/ha_organizer"
TARGET_DIR="/home/alves-dev/projects/others/core/config/custom_components/ha_organizer"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Integration source not found: $SOURCE_DIR" >&2
  exit 1
fi

sudo mkdir -p "$TARGET_DIR"
sudo find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
sudo cp -a "$SOURCE_DIR"/. "$TARGET_DIR"/

echo "Copied ha_organizer to $TARGET_DIR"
