#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ensure_frontend_deps() {
  if [ ! -d "$ROOT_DIR/frontend/node_modules" ] || \
    [ "$ROOT_DIR/frontend/package-lock.json" -nt "$ROOT_DIR/frontend/node_modules/.package-lock.json" ]; then
    echo "Installing frontend dependencies..."
    (cd "$ROOT_DIR/frontend" && npm ci)
  fi
}

ensure_backend_deps() {
  if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
    echo "Creating backend virtual environment..."
    (cd "$ROOT_DIR/backend" && uv venv)
  fi
  (cd "$ROOT_DIR/backend" && uv sync --dev)
}

start_frontend() {
  echo "Starting frontend dev server..."
  cd "$ROOT_DIR/frontend"
  npm run dev
}

start_backend() {
  echo "Starting backend dev server..."
  cd "$ROOT_DIR/backend"
  if [ -f ".env" ]; then
    uv run uvicorn app.main:app --reload --port 8000 --env-file .env
  else
    uv run uvicorn app.main:app --reload --port 8000
  fi
}

ensure_frontend_deps
ensure_backend_deps

start_frontend &
frontend_pid=$!

start_backend &
backend_pid=$!

trap 'kill "$frontend_pid" "$backend_pid" 2>/dev/null' INT TERM EXIT

wait "$frontend_pid" "$backend_pid"
