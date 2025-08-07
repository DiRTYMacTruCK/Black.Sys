#!/bin/bash

# Path to the virtual environment and script
VENV_DIR="./venv"
SCRIPT_PATH="./create_torrents.py"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Run: python3 -m venv $VENV_DIR && $VENV_DIR/bin/pip install torf"
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Activate virtual environment and run script
source "$VENV_DIR/bin/activate"
python3 "$SCRIPT_PATH"
deactivate
