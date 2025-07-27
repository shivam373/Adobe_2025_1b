# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies (Tesseract, poppler-utils, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install CPU-only torch from official PyTorch index
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload the sentence-transformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Download NLTK stopwords
RUN python -c "import nltk; nltk.download('stopwords')"

# Copy application code
COPY . .

# Set environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Run your script
CMD ["python", "run.py"]

