

#!/bin/bash

# Start ngrok tunnel for local FastAPI server (port 8000)
echo "Starting ngrok on port 8000..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null
then
    echo "❌ ngrok not found. Please install it first: https://ngrok.com/download"
    exit 1
fi

# Launch ngrok with default config or fallback
ngrok http 8000