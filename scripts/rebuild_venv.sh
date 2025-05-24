#!/bin/bash

# Rebuild Python virtual environment

echo "Removing existing virtual environment (if any)..."
rm -rf env

echo "Creating new virtual environment..."
python3 -m venv env

echo "Activating virtual environment..."
source env/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "✅ Virtual environment rebuilt and ready."
