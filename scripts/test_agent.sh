#!/bin/bash

echo "🧪 Running test_agent.sh..."
bash ./test_agent.sh

if [ $? -ne 0 ]; then
  echo "❌ Tests failed. Deployment aborted."
  exit 1
fi


echo "🚀 Tests passed. Starting deployment..."

# Run vector reindexing
echo "🔁 Running vector reindexing..." | tee -a "$LOG_FILE"
bash ./scripts/reindex_vectors.sh 2>&1 | tee -a "$LOG_FILE"

# Commit deployment state to Git
echo "📦 Committing deployment state to Git..." | tee -a "$LOG_FILE"
git add . && git commit -m "🧪 Successful test and deployment" | tee -a "$LOG_FILE"

# Push to remote repository
echo "📤 Pushing to remote repository..." | tee -a "$LOG_FILE"
git push | tee -a "$LOG_FILE"

# Define log file
LOG_FILE="./deployment.log"

# Start FastAPI app using uvicorn and log output
echo "📦 Launching FastAPI application..." | tee -a "$LOG_FILE"
uvicorn web.main:app --reload 2>&1 | tee -a "$LOG_FILE"