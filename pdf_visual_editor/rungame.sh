#!/bin/bash
# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check for .venv or venv
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    VENV_DIR=".venv"
fi

# Install requirements using the venv pip
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -r requirements.i386.txt

# Run the application using the venv python
echo "Starting PDF Visual Editor..."
"$VENV_DIR/bin/python" main.py
