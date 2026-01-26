#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  echo "Creating backend virtual environment..."
  (cd "$ROOT_DIR/backend" && uv venv)
fi

(cd "$ROOT_DIR/backend" && uv sync --dev)

echo "Formatting and checking backend..."
(cd "$ROOT_DIR/backend" && uv run ruff format .)
(cd "$ROOT_DIR/backend" && uv run ruff check .)
(cd "$ROOT_DIR/backend" && uv run mypy .)

if [ ! -d "$ROOT_DIR/frontend/node_modules" ] || \
  [ "$ROOT_DIR/frontend/package-lock.json" -nt "$ROOT_DIR/frontend/node_modules/.package-lock.json" ]; then
  echo "Installing frontend dependencies..."
  (cd "$ROOT_DIR/frontend" && npm ci)
fi

echo "Formatting and linting frontend..."
(cd "$ROOT_DIR/frontend" && npm run format)
(cd "$ROOT_DIR/frontend" && npm run lint)
