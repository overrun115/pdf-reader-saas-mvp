FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app:/app/shared:${PYTHONPATH}"

# Set work directory
WORKDIR /app

# Install system dependencies for enterprise features
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libmagic1 \
        libgl1-mesa-glx \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-spa \
        tesseract-ocr-fra \
        tesseract-ocr-deu \
        libreoffice \
        pandoc \
        poppler-utils \
        libxml2-dev \
        libxslt-dev \
        libssl-dev \
        libffi-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libgdk-pixbuf2.0-dev \
        libffi-dev \
        shared-mime-info \
        curl \
        wget \
        git \
        redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_minimal.txt .

# Install dependencies in stages to optimize caching
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Download spaCy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download es_core_news_sm || true

# Copy project
COPY . .
COPY ../shared /app/shared

# Create necessary directories
RUN mkdir -p /app/uploads \
    /app/data_platform \
    /app/logs \
    /app/temp \
    /app/exports

# Set proper permissions
RUN chmod +x /app/uploads /app/data_platform /app/logs /app/temp /app/exports

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]