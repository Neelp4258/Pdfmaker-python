# Multi-stage Dockerfile for HTML2PDF service with Playwright and Chromium
# Stage 1: Base image with Python and system dependencies
FROM python:3.11-slim as base

# Install system dependencies required by Playwright and Chromium
RUN apt-get update && apt-get install -y \
    # Basic tools
    wget \
    curl \
    gnupg \
    ca-certificates \
    # Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Fonts for better rendering
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Install Python dependencies
FROM base as dependencies

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Stage 3: Application image
FROM dependencies as application

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p /tmp/html2pdf && chmod 777 /tmp/html2pdf

# Create non-root user for security
RUN useradd -m -u 1000 pdfuser && \
    chown -R pdfuser:pdfuser /app /tmp/html2pdf

# Switch to non-root user
USER pdfuser

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/home/pdfuser/.cache/ms-playwright

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command (can be overridden)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]


# Worker image variant
FROM application as worker

# Override command for Celery worker
CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info", "--concurrency=4", "--max-tasks-per-child=50"]


# Development image variant
FROM dependencies as development

COPY . .

RUN mkdir -p /tmp/html2pdf && chmod 777 /tmp/html2pdf

ENV FLASK_ENV=development \
    PYTHONUNBUFFERED=1 \
    DEBUG=True

EXPOSE 5000

CMD ["python", "app.py"]
