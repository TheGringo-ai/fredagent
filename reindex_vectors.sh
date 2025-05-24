

#!/bin/bash
set -e

# Usage: ./reindex_vectors.sh
# This script clears and rebuilds the vector index from logs and documents.

echo "🔄 Reindexing vector database..."

# Safety check: ensure you're in the project root
if [ ! -d "memory" ]; then
  echo "❌ Error: This script must be run from the project root directory."
  exit 1
fi

# Check for vector_retriever.py existence
if [ ! -f "memory/vector_retriever.py" ]; then
  echo "❌ Error: vector_retriever.py not found!"
  exit 1
fi

# Step 1: Clear old vector index
VECTOR_DIR="memory/vector_index"
if [ -d "$VECTOR_DIR" ]; then
  echo "🧹 Removing old vector index at $VECTOR_DIR..."
  rm -rf "$VECTOR_DIR"
else
  echo "ℹ️ No existing vector index found. Skipping cleanup."
fi

# Step 2: Rebuild vector index
echo "⚙️ Rebuilding vector index from logs and documents..."
mkdir -p logs
python3 memory/vector_retriever.py --reindex >> logs/reindex.log 2>&1

echo "✅ Reindexing complete."