#!/bin/bash

# Configuration
ENV_DIR="env"
BACKUP_DIR=".env_backup"
NODE_DIR="node_modules"

echo "⚠️ This will delete and recreate your Python virtual environment and optionally your frontend environment."

read -p "Do you want to proceed with the full reset? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
  echo "❌ Aborted."
  exit 1
fi

# Backup logic
if [[ -d "$ENV_DIR" ]]; then
  echo "📦 Backing up existing environment to $BACKUP_DIR..."
  rm -rf "$BACKUP_DIR"
  mv "$ENV_DIR" "$BACKUP_DIR"
fi

# Auto-detect Python version
PYTHON_BIN=$(command -v python3 || command -v python)
if [[ -z "$PYTHON_BIN" ]]; then
  echo "❌ Python is not installed or not in PATH."
  exit 1
fi

echo "🔄 Creating new virtual environment using $PYTHON_BIN..."
$PYTHON_BIN -m venv "$ENV_DIR"

echo "✅ Activating new environment..."
source "$ENV_DIR/bin/activate"

echo "⬆️ Upgrading pip and installing requirements..."
pip install --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  echo "⚠️ No requirements.txt found, skipping Python dependency installation."
fi

# Frontend reset
if [[ -f package.json ]]; then
  echo "🧹 Cleaning up frontend environment..."
  rm -rf "$NODE_DIR"
  echo "📦 Reinstalling frontend dependencies..."
  npm install
else
  echo "ℹ️ No package.json found, skipping frontend reset."
fi

echo "🎉 Environment reset complete."
