

#!/bin/bash

echo "📦 Git Auto Commit & Push Utility"

# Ensure we're in a Git repo
if [ ! -d .git ]; then
  echo "❌ Not a Git repository. Exiting."
  exit 1
fi

# Detect changes
if git diff --quiet && git diff --cached --quiet; then
  echo "✅ No changes to commit."
  exit 0
fi

# Prompt for commit message
read -p "📝 Enter commit message: " message

# Stage all changes
git add .

# Commit
git commit -m "$message"

# Push to current branch
branch=$(git rev-parse --abbrev-ref HEAD)
echo "🚀 Pushing to branch '$branch'..."
git push origin "$branch"