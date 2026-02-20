#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQ_FILE="$ROOT_DIR/requirements.txt"
PIDFILE="$ROOT_DIR/server.pid"
LOGFILE="$ROOT_DIR/server.log"

usage() {
  cat <<EOF
Usage: $0 {install|start|bg|stop|status|help}

Commands:
  install   Create venv (if missing) and install Python deps
  start     Start Flask in foreground (uses venv if present)
  bg        Start Flask in background, write PID to server.pid
  stop      Stop background server (uses server.pid)
  status    Check port 8000 and show pid/log info
  help      Show this message
EOF
  exit 1
}

create_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi
}

activate_venv() {
  if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
  fi
}

install_deps() {
  if [ -f "$REQ_FILE" ]; then
    echo "Installing Python requirements from $REQ_FILE"
    pip install -r "$REQ_FILE"
  else
    echo "No requirements.txt found at $REQ_FILE"
    return 1
  fi
}

start_fg() {
  export FLASK_APP=server.endpoints
  echo "Starting Flask (foreground) on 127.0.0.1:8000"
  python3 -m flask run --host=127.0.0.1 --port=8000
}

start_bg() {
  export FLASK_APP=server.endpoints
  echo "Starting Flask (background) on 127.0.0.1:8000, logs -> $LOGFILE"
  nohup python3 -m flask run --host=127.0.0.1 --port=8000 > "$LOGFILE" 2>&1 &
  echo $! > "$PIDFILE"
  echo "PID $(cat "$PIDFILE") written to $PIDFILE"
}

stop_server() {
  if [ -f "$PIDFILE" ]; then
    pid=$(cat "$PIDFILE")
    echo "Stopping PID $pid"
    kill "$pid" || true
    rm -f "$PIDFILE"
  else
    echo "No pidfile ($PIDFILE) found"
  fi
}

status() {
  if lsof -iTCP:8000 -sTCP:LISTEN -P -n >/dev/null 2>&1; then
    echo "Port 8000 is LISTENING"
    lsof -iTCP:8000 -sTCP:LISTEN -P -n
  else
    echo "Port 8000 is free"
  fi
  if [ -f "$PIDFILE" ]; then
    echo "PID file: $PIDFILE -> $(cat "$PIDFILE")"
  fi
  echo "Log file: $LOGFILE"
}

if [ $# -lt 1 ]; then
  usage
fi

cmd=$1

case "$cmd" in
  install)
    create_venv
    activate_venv
    install_deps
    ;;
  start)
    create_venv || true
    activate_venv || true
    start_fg
    ;;
  bg)
    create_venv || true
    activate_venv || true
    start_bg
    ;;
  stop)
    stop_server
    ;;
  status)
    status
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $cmd"
    usage
    ;;
esac
