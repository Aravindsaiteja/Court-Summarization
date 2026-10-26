# Dockerfile for Real-Time Multilingual Court Proceeding Summarizer
FROM python:3.10-slim

# System level dependencies: FFmpeg and audio libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency manifest
COPY requirements.txt .

# Install pinned Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download required NLTK tokenizers
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

# Copy full application codebase
COPY . .

# Expose ports: 8000 for FastAPI backend, 8501 for Streamlit UI
EXPOSE 8000 8501

# Default command launches FastAPI backend
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
