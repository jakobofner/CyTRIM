#!/bin/bash
# Start the extended CyTRIM GUI with all advanced features

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the extended GUI
python pytrim_gui_extended.py
