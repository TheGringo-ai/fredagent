#!/bin/bash

# Utility script to start AI agent using Uvicorn

ENV_DIR=env

echo -e "\033[1;34m[INFO]\033[0m Checking for virtual environment..."
if [ -d "$ENV_DIR/bin" ]; then
    echo -e "\033[1;32m[INFO]\033[0m Virtual environment found."
else
    echo -e "\033[1;33m[INFO]\033[0m Creating virtual environment..."
    python3 -m venv $ENV_DIR
fi

echo -e "\033[1;34m[INFO]\033[0m Activating virtual environment..."
source $ENV_DIR/bin/activate

if [ -f "requirements.txt" ]; then
    echo -e "\033[1;34m[INFO]\033[0m Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "\033[1;31m[WARNING]\033[0m requirements.txt not found."
fi

if ! command -v uvicorn &> /dev/null; then
    echo -e "\033[1;31m[ERROR]\033[0m Uvicorn is not installed. Installing..."
    pip install uvicorn
fi

if [ ! -f "web/main.py" ]; then
    echo -e "\033[1;31m[ERROR]\033[0m web/main.py not found. Aborting."
    exit 1
fi

echo -e "\033[1;34m[INFO]\033[0m Opening browser at http://127.0.0.1:8000"
open http://127.0.0.1:8000

echo -e "\033[1;34m[INFO]\033[0m Starting Uvicorn server with live reload..."
uvicorn web.main:app --reload --reload-dir .

echo -e "\033[1;32m[SUCCESS]\033[0m AI agent launched."
