#!/bin/bash

echo "🚨 Cleaning Gringo AI Ops project folder..."

MODE=$1

if [[ "$MODE" != "--deep" && "$MODE" != "--light" && "$MODE" != "--nuke" ]]; then
  echo "Usage: $0 [--light | --deep | --nuke]"
  echo "  --light   Remove only .pyc, logs, and __pycache__"
  echo "  --deep    Full cleanup (node_modules, env, build, Tailwind, coverage, etc.)"
  echo "  --nuke    Deep cleanup plus remove .git, databases, logs/, snapshots, env files, and egg-info"
  exit 1
fi

read -p "⚠️ Are you sure you want to proceed with $MODE cleanup? [y/N]: " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Cleanup canceled."
  exit 1
fi

if [[ "$MODE" == "--deep" ]]; then
  echo "🔧 Performing deep cleanup..."
  rm -rf node_modules env .venv dist build
  rm -f web/static/style.css
  rm -f web/static/*.css
  rm -rf .mypy_cache .coverage coverage.xml
fi

if [[ "$MODE" == "--nuke" ]]; then
  echo "💥 Performing nuke cleanup..."
  rm -rf node_modules env .venv dist build
  rm -f web/static/style.css
  rm -f web/static/*.css
  rm -rf .mypy_cache .coverage coverage.xml
  rm -rf .git logs __snapshots__
  find . -type f \( -name '*.db' -o -name '*.sqlite3' -o -name '.env' -o -name '.env.local' \) -delete
  find . -type d -name '*.egg-info' -exec rm -rf {} +
fi

# Common cleanup for both modes
echo "🧹 Removing Python caches and junk files..."
find . -type d -name '__pycache__' -exec rm -rf {} +
find . -type d -name '.pytest_cache' -exec rm -rf {} +
find . -type d -name '.cache' -exec rm -rf {} +
find . -name '*.pyc' -delete
find . -name '.DS_Store' -delete
find . -name '*.log' -delete

echo "✅ Cleanup complete."
