#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONGO_PORT="27017"
API_PORT="8000"

usage() {
  cat <<EOF
Usage: $0 {up|start|seed|status|stop|help}

Commands:
  up      Start MongoDB (Homebrew), backend, and seed city data (default)
  start   Start MongoDB + backend (no seeding)
  seed    Seed city data from data/bkup/cities.json
  status  Show MongoDB/backend status
  stop    Stop backend only
  help    Show this help
EOF
}

is_port_listening() {
  local port="$1"
  lsof -iTCP:"$port" -sTCP:LISTEN -P -n >/dev/null 2>&1
}

ensure_mongo() {
  if is_port_listening "$MONGO_PORT"; then
    echo "MongoDB already listening on port $MONGO_PORT"
    return
  fi

  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Install/start MongoDB manually, then rerun."
    exit 1
  fi

  if ! brew list --versions mongodb-community@7.0 >/dev/null 2>&1; then
    echo "MongoDB not installed via Homebrew. Install with:"
    echo "  brew tap mongodb/brew && brew install mongodb-community@7.0"
    exit 1
  fi

  echo "Starting MongoDB service..."
  brew services start mongodb/brew/mongodb-community@7.0 >/dev/null || true

  for _ in {1..20}; do
    if is_port_listening "$MONGO_PORT"; then
      echo "MongoDB is up on port $MONGO_PORT"
      return
    fi
    sleep 0.5
  done

  echo "MongoDB did not start in time."
  exit 1
}

start_backend() {
  echo "Installing backend deps (venv)..."
  "$ROOT_DIR/run-backend.sh" install

  echo "Restarting backend..."
  "$ROOT_DIR/run-backend.sh" stop || true
  lsof -tiTCP:"$API_PORT" -sTCP:LISTEN 2>/dev/null | xargs -r kill || true
  "$ROOT_DIR/run-backend.sh" bg

  for _ in {1..20}; do
    if is_port_listening "$API_PORT"; then
      echo "Backend is up on http://127.0.0.1:$API_PORT"
      return
    fi
    sleep 0.5
  done

  echo "Backend failed to start. Check server.log"
  exit 1
}

seed_data() {
  if [ ! -f "$ROOT_DIR/.venv/bin/activate" ]; then
    echo "No virtualenv found at $ROOT_DIR/.venv. Run start/up first."
    exit 1
  fi

  echo "Seeding cities data..."
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.venv/bin/activate"
  python "$ROOT_DIR/load_geo_script.py"
}

status_all() {
  echo "--- MongoDB ---"
  if is_port_listening "$MONGO_PORT"; then
    lsof -iTCP:"$MONGO_PORT" -sTCP:LISTEN -P -n
  else
    echo "MongoDB is not listening on $MONGO_PORT"
  fi

  echo
  echo "--- Backend ---"
  "$ROOT_DIR/run-backend.sh" status

  echo
  echo "--- /cities check ---"
  if is_port_listening "$API_PORT"; then
    python3 - <<'PY'
import json
import urllib.request

url = "http://127.0.0.1:8000/cities"
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        data = json.loads(r.read().decode("utf-8"))
    print(f"GET /cities OK, Number of cities: {data.get('Number of cities', 'unknown')}")
except Exception as e:
    print(f"GET /cities failed: {e}")
PY
  else
    echo "Backend is not running"
  fi
}

cmd="${1:-up}"
case "$cmd" in
  up)
    ensure_mongo
    start_backend
    seed_data
    status_all
    ;;
  start)
    ensure_mongo
    start_backend
    status_all
    ;;
  seed)
    seed_data
    ;;
  status)
    status_all
    ;;
  stop)
    "$ROOT_DIR/run-backend.sh" stop
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $cmd"
    usage
    exit 1
    ;;
esac
