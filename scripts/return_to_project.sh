#!/bin/bash

# Navigate back to the project root directory
cd "$(dirname "$0")" || {
    echo "Failed to locate the script directory."
    exit 1
}

PROJECT_ROOT=$(pwd)

echo "Navigated to project root at: $PROJECT_ROOT"
