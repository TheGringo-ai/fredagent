#!/bin/bash
# export_tokens.sh
# Use this script to export all required API keys and secrets into your environment.

echo "Exporting API tokens..."

export OPENAI_API_KEY="your-openai-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"
export FIREBASE_API_KEY="your-firebase-api-key-here"

echo "Tokens exported. Make sure this script is sourced, not executed."

# Usage: source ./export_tokens.sh