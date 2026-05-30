#!/usr/bin/env sh
set -eu

# Activate venv if it exists
if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
fi

PYTHONPATH=. python3 -m chessbot.main "$@"
