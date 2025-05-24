#!/bin/bash

# Utility script: scripts/start.sh
# To make this script executable, run:
# chmod +x scripts/start.sh

ENV_DIR=env

echo "Checking for virtual environment..."
if [ -d "$ENV_DIR/bin" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3 -m venv $ENV_DIR
fi

echo "Activating virtual environment..."
source $ENV_DIR/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found!"
fi

echo "Launching AI agent dashboard with Uvicorn..."
echo "Opening browser at http://127.0.0.1:8000"
open http://127.0.0.1:8000
echo "[INFO] Starting Uvicorn server with --reload for live code updates..."
uvicorn web.main:app --reload

echo "[SUCCESS] AI agent started via utility script."
