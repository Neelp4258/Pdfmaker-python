# Multi-stage Dockerfile for HTML2PDF service with Playwright and Chromium
# Optimized to fix Playwright installation issues

# Stage 1: Base image with Python and ALL system dependencies
FROM python:3.11-slim as base

# Set environment to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install ALL system dependencies in one go
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential build tools
    build-essential \
    # Basic utilities
    wget \
    curl \
    gnupg \
    ca-certificates \
    git \
    # Chromium/Playwright dependencies (COMPLETE LIST)
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
    libglib2.0-0 \
    libgtk-3-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxext6 \
    # Additional libraries that might be missing
    libgconf-2-4 \
    libnss3-dev \
    libxss1 \
    # Fonts for better rendering
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    ttf-mscorefonts-installer \
    fontconfig \
    # Clean up to reduce image size
    && fc-cache -f \
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

# IMPORTANT: Install Playwright system dependencies FIRST
# This installs OS-level dependencies that Playwright needs
RUN playwright install-deps chromium

# Then install Playwright browsers with retry logic
# Set environment to ensure proper installation
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN python -m playwright install chromium --with-deps || \
    (echo "First attempt failed, retrying..." && sleep 5 && python -m playwright install chromium --with-deps) || \
    (echo "Second attempt failed, trying without --with-deps..." && python -m playwright install chromium)

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
