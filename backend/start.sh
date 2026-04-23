#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source environment variables if .env exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Prefer venv python if available
PYTHON="${SCRIPT_DIR}/venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
fi

# Start the FastAPI backend
exec "$PYTHON" main.py
