#!/bin/sh
# Start the local Home Assistant instance used to test Activity Tracker.

set -eu

readonly HA_CORE_DIR="/home/alves-dev/projects/others/core"
readonly HA_CONFIG_DIR="$HA_CORE_DIR/config"
readonly PID_FILE="/tmp/ha-activity-tracker-home-assistant.pid"
readonly LOG_FILE="/tmp/ha-activity-tracker-home-assistant.log"
readonly HEALTH_URL="http://127.0.0.1:8123/"
readonly START_TIMEOUT_SECONDS=30

is_home_assistant_process() {
  process_args="$(ps -p "$1" -o args= 2>/dev/null || true)"
  case "$process_args" in
    *homeassistant*"$HA_CONFIG_DIR"*) return 0 ;;
    *) return 1 ;;
  esac
}

if [ ! -d "$HA_CORE_DIR" ] || [ ! -d "$HA_CONFIG_DIR" ]; then
  echo "Home Assistant core/config directory was not found." >&2
  exit 1
fi

if [ -r "$PID_FILE" ]; then
  pid="$(cat "$PID_FILE")"
  case "$pid" in
    *[!0-9]*|'') valid_pid=false ;;
    *) valid_pid=true ;;
  esac
  if [ "$valid_pid" = true ] && is_home_assistant_process "$pid"; then
    echo "Home Assistant is already running (PID $pid)."
    exit 0
  fi
  rm -f "$PID_FILE"
fi

cd "$HA_CORE_DIR"
# Do not let the Activity Tracker virtual environment override Home Assistant's.
unset VIRTUAL_ENV

# A distinct session lets the local instance survive the shell that launched it.
nohup setsid uv run --project . python -m homeassistant --config "$HA_CONFIG_DIR" \
  >"$LOG_FILE" 2>&1 &
pid=$!
echo "$pid" >"$PID_FILE"

elapsed=0
while [ "$elapsed" -lt "$START_TIMEOUT_SECONDS" ]; do
  if ! is_home_assistant_process "$pid"; then
    rm -f "$PID_FILE"
    echo "Home Assistant stopped during startup. See $LOG_FILE." >&2
    exit 1
  fi
  if curl -fsS --max-time 1 "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Home Assistant started (PID $pid)."
    echo "Log: $LOG_FILE"
    exit 0
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done

echo "Home Assistant did not become ready within $START_TIMEOUT_SECONDS seconds." >&2
echo "See $LOG_FILE." >&2
exit 1
