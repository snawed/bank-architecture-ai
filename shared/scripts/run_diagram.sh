#!/bin/bash

set -euo pipefail

DOMAIN=$1
DIAGRAM_LEVEL=$2
PYTHON_BIN=".venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "Running $DIAGRAM_LEVEL generation for $DOMAIN"

"$PYTHON_BIN" shared/scripts/generate_diagram.py "$DOMAIN" "$DIAGRAM_LEVEL"

mmdc -i "$DOMAIN/diagrams/$DIAGRAM_LEVEL.mmd" \
     -o "$DOMAIN/diagrams/$DIAGRAM_LEVEL.svg"
