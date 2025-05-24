

#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define project root (adjust if needed)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting local deployment..."

# Activate virtual environment if it exists
if [ -d "env" ]; then
    source env/bin/activate
    echo "✅ Virtual environment activated."
else
    echo "⚠️  No virtual environment found. Please run setup_env.sh first."
    exit 1
fi

# Run Uvicorn with FastAPI app
APP_MODULE="web.main:app"
PORT=8000

echo "📡 Launching Uvicorn server at http://127.0.0.1:$PORT ..."
exec uvicorn "$APP_MODULE" --reload --port $PORT