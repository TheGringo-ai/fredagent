#!/bin/bash

echo "🔧 Fixing Gringo AI Ops environment..."

# Activate the Conda environment
echo "🔄 Activating conda environment 'gringo-env'..."
source ~/micromamba/etc/profile.d/micromamba.sh
micromamba activate gringo-env

# Reinstall critical dependencies
echo "📦 Reinstalling key packages..."
pip install --force-reinstall "openai==1.82.0" "fastapi==0.103.2" "starlette<0.28.0,>=0.27.0"
pip install sentence-transformers huggingface_hub==0.16.4

# Handle faiss explicitly
echo "📌 Ensuring faiss-cpu is correctly installed..."
conda install -c conda-forge faiss-cpu=1.9.0 --yes

# Check for missing directories
echo "📁 Verifying memory module dependencies..."
mkdir -p web/memory/agents
mkdir -p web/memory

# Touch missing Python files
touch web/memory/plan_executor.py
touch web/memory/agents/dev_assistant.py

echo "✅ Environment fix complete. You can now restart your server."