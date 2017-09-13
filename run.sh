#!/usr/bin/env bash

if [ ! -f config.py ]; then
  echo "No config.py found. Copy config.py.examples and edit it by yourself."
  exit 0
fi

python3 main.py
