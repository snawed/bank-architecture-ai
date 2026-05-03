#!/bin/bash

set -euo pipefail

DOMAIN=$1
PYTHON_BIN=".venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "Running C1 generation for $DOMAIN"

"$PYTHON_BIN" shared/scripts/generate_diagram.py "$DOMAIN" "C1"

mmdc -i "$DOMAIN/diagrams/C1.mmd" \
     -o "$DOMAIN/diagrams/C1.svg"
