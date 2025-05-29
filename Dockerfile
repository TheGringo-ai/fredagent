# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Preload required Hugging Face models to prevent runtime downloads
RUN python -c "\
from transformers import pipeline, AutoModel, AutoTokenizer; \
pipeline('summarization', model='sshleifer/distilbart-cnn-12-6'); \
AutoTokenizer.from_pretrained('bert-base-uncased'); \
AutoModel.from_pretrained('bert-base-uncased')"

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]

