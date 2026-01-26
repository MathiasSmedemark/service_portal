#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  echo "Creating backend virtual environment..."
  (cd "$ROOT_DIR/backend" && uv venv)
fi

(cd "$ROOT_DIR/backend" && uv sync --dev)

echo "Running backend tests..."
(cd "$ROOT_DIR/backend" && uv run pytest -q)

if [ ! -d "$ROOT_DIR/frontend/node_modules" ] || \
  [ "$ROOT_DIR/frontend/package-lock.json" -nt "$ROOT_DIR/frontend/node_modules/.package-lock.json" ]; then
  echo "Installing frontend dependencies..."
  (cd "$ROOT_DIR/frontend" && npm ci)
fi

echo "Running frontend tests..."
(cd "$ROOT_DIR/frontend" && npm test)
