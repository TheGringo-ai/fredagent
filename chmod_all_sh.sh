#!/bin/bash

echo "🔐 Making all .sh scripts in ./scripts executable..."

for file in ./scripts/*.sh; do
  if [ -f "$file" ]; then
    chmod +x "$file"
    echo "✅ Set executable: $file"
  fi
done

echo "🚀 Done. All scripts are now executable."
