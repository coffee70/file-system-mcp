#!/usr/bin/env bash
set -e

export WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(pwd)}"
export ENABLE_WRITES="${ENABLE_WRITES:-false}"

uvicorn app.main:app --host 0.0.0.0 --port 8000