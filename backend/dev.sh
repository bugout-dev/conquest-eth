#!/usr/bin/env sh

# Expects access to Python environment with the requirements for this project installed.
set -e

CEM_BACKEND_HOST="${CEM_BACKEND_HOST:-0.0.0.0}"
CEM_BACKEND_PORT="${CEM_BACKEND_PORT:-9898}"

uvicorn --port "$CEM_BACKEND_PORT" --host "$CEM_BACKEND_HOST" backend.api:app --reload
