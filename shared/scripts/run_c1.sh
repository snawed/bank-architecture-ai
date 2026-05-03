#!/bin/bash

DOMAIN=$1

echo "Running C1 generation for $DOMAIN"

python shared/scripts/generate_c1.py $DOMAIN

mmdc -i $DOMAIN/diagrams/C1.mmd \
     -o $DOMAIN/diagrams/C1.svg