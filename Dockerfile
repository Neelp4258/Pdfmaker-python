# Multi-stage Dockerfile for HTML2PDF service with Playwright and Chromium
# Simplified approach using Playwright's built-in dependency management

# Stage 1: Base image with minimal system dependencies
FROM python:3.11-slim as base

# Set environment to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal essential utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Install Python dependencies and Playwright
FROM base as dependencies

# Copy requirements first for layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Set Playwright environment
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright with all system dependencies using Playwright's installer
# This automatically handles all required system packages
RUN playwright install --with-deps chromium

# Verify installation
RUN python -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully')"

# Stage 3: Application image
FROM dependencies as application

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p /tmp/html2pdf /app/data/pdfs && \
    chmod 777 /tmp/html2pdf /app/data/pdfs

# Create non-root user for security
RUN useradd -m -u 1000 pdfuser && \
    chown -R pdfuser:pdfuser /app /tmp/html2pdf

# DON'T switch user yet - keep as root for broader compatibility
# USER pdfuser

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]


# Worker image variant
FROM application as worker

# Override command for Celery worker
CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info", "--concurrency=4", "--max-tasks-per-child=50"]


# Development image variant
FROM dependencies as development

COPY . .

RUN mkdir -p /tmp/html2pdf /app/data/pdfs && \
    chmod 777 /tmp/html2pdf /app/data/pdfs

ENV FLASK_ENV=development \
    PYTHONUNBUFFERED=1 \
    DEBUG=True \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

EXPOSE 5000

CMD ["python", "app.py"]
