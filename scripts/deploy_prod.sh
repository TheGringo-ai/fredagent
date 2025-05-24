

#!/bin/bash

echo "🔄 Deploying to production..."

# Set project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit

# Activate virtual environment
if [ -d "env" ]; then
  source env/bin/activate
else
  echo "⚠️ Virtual environment not found. Run ./scripts/rebuild_venv.sh first."
  exit 1
fi

# Run pre-deployment tests
echo "✅ Running tests..."
./scripts/run_tests.sh || { echo '❌ Tests failed. Aborting.'; exit 1; }

# Collect static files (if using any)
echo "📦 Collecting static files..."
mkdir -p static_build
cp -r web/static/* static_build/ 2>/dev/null

# Git commit and push (optional)
echo "🔐 Committing changes..."
git add .
git commit -m "🔧 Automated deploy commit"
git push

# Deployment command (placeholder: customize for GCP, Fly.io, etc.)
echo "🚀 Starting production server..."
uvicorn web.main:app --host 0.0.0.0 --port 8080

echo "✅ Deployment complete."