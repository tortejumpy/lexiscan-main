# Dockerfile for LexiScan Auto — compatible with Hugging Face Spaces
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install production requirements only (no TensorFlow/Spacy)
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/processed

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Run API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
