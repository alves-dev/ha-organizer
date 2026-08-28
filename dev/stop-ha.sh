#!/bin/sh
# Stop the local Home Assistant instance started by start-ha.sh.

set -eu

readonly PID_FILE="/tmp/ha-local-home-assistant.pid"
readonly STOP_TIMEOUT_SECONDS=30
readonly HA_CONFIG_DIR="/home/alves-dev/projects/others/core/config"

is_home_assistant_process() {
  process_args="$(ps -p "$1" -o args= 2>/dev/null || true)"
  case "$process_args" in
    *homeassistant*"$HA_CONFIG_DIR"*) return 0 ;;
    *) return 1 ;;
  esac
}

if [ ! -r "$PID_FILE" ]; then
  echo "No Home Assistant PID file found; nothing to stop."
  exit 0
fi

pid="$(cat "$PID_FILE")"
case "$pid" in
  *[!0-9]*|'') valid_pid=false ;;
  *) valid_pid=true ;;
esac
if [ "$valid_pid" = false ] || ! is_home_assistant_process "$pid"; then
  rm -f "$PID_FILE"
  echo "No matching Home Assistant process is running."
  exit 0
fi

kill -TERM "$pid"
elapsed=0
while [ "$elapsed" -lt "$STOP_TIMEOUT_SECONDS" ]; do
  if ! is_home_assistant_process "$pid"; then
    rm -f "$PID_FILE"
    echo "Home Assistant stopped."
    exit 0
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done

echo "Home Assistant did not stop within $STOP_TIMEOUT_SECONDS seconds (PID $pid)." >&2
exit 1
