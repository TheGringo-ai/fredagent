

#!/bin/bash

echo "🔍 Running tests..."

# Activate the virtual environment if not already active
if [ -f "env/bin/activate" ]; then
  source env/bin/activate
fi

# Check if pytest is installed and run it, otherwise fall back to syntax checks
if command -v pytest &> /dev/null; then
    pytest
else
    echo "⚠️  Pytest is not installed. Running syntax check instead..."
    find . -name "*.py" -not -path "./env/*" -exec python -m py_compile {} +
fi