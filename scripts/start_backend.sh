#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"
exec uvicorn backend.app.main:app --host "${PYXIS_API_HOST:-127.0.0.1}" --port "${PYXIS_API_PORT:-8000}"
