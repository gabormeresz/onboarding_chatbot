#!/bin/bash
# Quick script to run evaluation with correct PYTHONPATH

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Running evaluation from: $PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/src" uv run python eval/run_eval.py "$@"
