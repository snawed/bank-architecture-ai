#!/bin/bash

set -euo pipefail

PYTHON_BIN=".venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m shared.ui.architecture_ui
