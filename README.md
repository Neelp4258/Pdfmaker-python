# HTML2PDF Service 🚀

Production-ready Python Flask service for converting HTML/URLs to pixel-perfect PDFs using headless Chromium (Playwright).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/Pdfmaker-python)
[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/template/html2pdf)
[![Deploy to Fly.io](https://fly.io/static/images/speedrun/app.webp)](https://fly.io/docs/speedrun/)

## Features ✨

- **Modern Web UI**: Beautiful, intuitive interface with HTML editor, live preview, and job tracking
- **Pixel-Perfect Rendering**: Uses Playwright with headless Chromium for accurate PDF generation
- **Flexible Page Sizing**: Named formats (A4, Letter, etc.), custom dimensions, and aspect ratios
- **Async Job Processing**: Celery + Redis for handling large/long-running conversions
- **Sync Endpoint**: Immediate response for small jobs
- **Batch Processing**: Queue multiple PDFs at once
- **Security First**: API key auth, rate limiting, SSRF protection, HTML sanitization
- **Scalable**: Docker/Kubernetes ready with worker pool management
- **Cloud Storage**: Local, AWS S3, and Google Cloud Storage support
- **Multi-page Support**: CSS page-break rules, custom margins, backgrounds
- **Configurable**: No artificial limits - everything is configurable

## Quick Start 🏃

### Docker Compose (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd Pdfmaker-python

# Copy environment file
cp .env.example .env

# Edit .env and set your API keys
nano .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:5000/health
```

The service will be available at:
- **Web UI**: `http://localhost:5000` - Beautiful interface for creating PDFs
- **API**: `http://localhost:5000` - REST API endpoints
- **API Docs**: `http://localhost:5000/docs` - Interactive API documentation
- **Celery Monitor**: `http://localhost:5555` - Flower monitoring dashboard

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start Redis
redis-server

# Start Flask app
python app.py

# In another terminal, start Celery worker
celery -A celery_worker.celery_app worker --loglevel=info
```

## Web Interface 🎨

The service includes a modern, feature-rich web interface:

### Features
- **CodeMirror Editor**: Syntax-highlighted HTML/CSS editing
- **Live Configuration**: Visual controls for all PDF options
- **Templates**: Pre-built templates for invoices, reports, resumes, presentations
- **Job History**: Track and download recent PDFs
- **Dark Mode**: Comfortable viewing in any environment
- **File Upload**: Import HTML files directly
- **Real-time Status**: Live job progress tracking
- **Responsive Design**: Works on desktop, tablet, and mobile

### Using the Web UI

1. **Open** `http://localhost:5000` in your browser
2. **Choose Input Mode**: HTML editor or URL input
3. **Configure Options**: Select format, orientation, margins, etc.
4. **Edit HTML**: Use the built-in editor or load a template
5. **Add Custom CSS**: Optional styling in the CSS panel
6. **Generate PDF**: Click "Generate PDF" button
7. **Download**: PDF downloads automatically or from job history

### Templates

Built-in templates for common use cases:
- **Invoice**: Professional invoice layout
- **Report**: Multi-page report with cover page
- **Resume**: Clean CV/resume design
- **Presentation**: 16:9 slide format

## API Documentation 📚

### Authentication

Include your API key in requests:
- Header: `X-API-Key: your-api-key`
- Query param: `?api_key=your-api-key`

### Endpoints

#### `POST /render-sync` - Synchronous Rendering

Returns PDF immediately (30s timeout by default).

**Request:**
```json
{
  "html": "<html>...</html>",
  "format": "A4",
  "landscape": false,
  "margin": "10mm",
  "scale": 1.0,
  "css": "body { color: blue; }"
}
```

**Response:** PDF file (application/pdf)

#### `POST /render` - Asynchronous Rendering

Queues job and returns job ID.

**Request:** Same as `/render-sync`

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "status_url": "/status/<job_id>"
}
```

#### `GET /status/<job_id>` - Job Status

Check rendering status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "download_url": "/download/<job_id>",
  "size_bytes": 12345
}
```

#### `GET /download/<job_id>` - Download PDF

Download generated PDF file.

#### `POST /batch` - Batch Rendering

Queue multiple jobs at once.

**Request:**
```json
{
  "jobs": [
    {"html": "...", "format": "A4"},
    {"url": "https://example.com", "format": "Letter"}
  ]
}
```

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `html` | string | HTML content (mutually exclusive with url) | `"<html>...</html>"` |
| `url` | string | URL to render (mutually exclusive with html) | `"https://example.com"` |
| `format` | string | Paper format | `"A4"`, `"Letter"`, `"Legal"`, `"receipt"` |
| `width` | string | Custom width | `"210mm"`, `"8.5in"`, `"800px"` |
| `height` | string | Custom height | `"297mm"`, `"11in"`, `"1200px"` |
| `aspect` | string | Aspect ratio | `"16:9"`, `"16:10"`, `"4:3"` |
| `landscape` | boolean | Landscape orientation | `true`, `false` |
| `margin` | string | Margins (CSS format) | `"10mm"` or `"10mm,20mm,10mm,20mm"` |
| `scale` | float | Page scale (0.1-2.0) | `1.0`, `0.8` |
| `page_ranges` | string | Pages to print | `"1-5, 8, 11-13"` |
| `css` | string | Additional CSS to inject | `"body { font-size: 14px; }"` |
| `wait_for` | string | Selector or timeout (ms) | `"#content"`, `"5000"` |
| `headers` | object | HTTP headers for URL requests | `{"User-Agent": "..."}` |

## Usage Examples 💡

### cURL Examples

#### Simple HTML to PDF
```bash
curl -X POST http://localhost:5000/render-sync \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello World</h1></body></html>",
    "format": "A4"
  }' \
  --output document.pdf
```

#### URL to PDF with Custom Size
```bash
curl -X POST http://localhost:5000/render-sync \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "width": "1920px",
    "height": "1080px",
    "scale": 0.5
  }' \
  --output webpage.pdf
```

#### Async Job with Receipt Format
```bash
# Queue job
JOB_ID=$(curl -X POST http://localhost:5000/render \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h2>Receipt</h2><p>Total: $42.00</p></body></html>",
    "format": "receipt",
    "margin": "5mm"
  }' | jq -r '.job_id')

# Check status
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/status/$JOB_ID

# Download when complete
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/download/$JOB_ID \
  --output receipt.pdf
```

#### 16:9 Presentation Format
```bash
curl -X POST http://localhost:5000/render-sync \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Slide 1</h1></body></html>",
    "aspect": "16:9",
    "landscape": true
  }' \
  --output slide.pdf
```

### Python Client Example

```python
import requests
import time

class HTML2PDFClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}

    def render_sync(self, html=None, url=None, **options):
        """Render PDF synchronously."""
        data = {**({"html": html} if html else {"url": url}), **options}
        response = requests.post(
            f"{self.base_url}/render-sync",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.content

    def render_async(self, html=None, url=None, **options):
        """Queue PDF rendering job."""
        data = {**({"html": html} if html else {"url": url}), **options}
        response = requests.post(
            f"{self.base_url}/render",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['job_id']

    def get_status(self, job_id):
        """Get job status."""
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def download(self, job_id):
        """Download PDF."""
        response = requests.get(
            f"{self.base_url}/download/{job_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.content

    def render_and_wait(self, html=None, url=None, timeout=300, **options):
        """Queue job and wait for completion."""
        job_id = self.render_async(html, url, **options)

        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)
            if status['status'] == 'completed':
                return self.download(job_id)
            elif status['status'] == 'failed':
                raise Exception(f"Rendering failed: {status.get('error')}")
            time.sleep(2)

        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

# Usage
client = HTML2PDFClient('http://localhost:5000', 'your-api-key')

# Sync rendering
pdf = client.render_sync(
    html='<h1>Invoice</h1><p>Total: $100</p>',
    format='A4',
    margin='20mm'
)
with open('invoice.pdf', 'wb') as f:
    f.write(pdf)

# Async rendering
pdf = client.render_and_wait(
    url='https://example.com',
    format='Letter',
    landscape=True
)
with open('webpage.pdf', 'wb') as f:
    f.write(pdf)
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');
const fs = require('fs');

class HTML2PDFClient {
  constructor(baseURL, apiKey) {
    this.client = axios.create({
      baseURL,
      headers: { 'X-API-Key': apiKey }
    });
  }

  async renderSync(options) {
    const response = await this.client.post('/render-sync', options, {
      responseType: 'arraybuffer'
    });
    return Buffer.from(response.data);
  }

  async renderAsync(options) {
    const response = await this.client.post('/render', options);
    return response.data.job_id;
  }

  async getStatus(jobId) {
    const response = await this.client.get(`/status/${jobId}`);
    return response.data;
  }

  async download(jobId) {
    const response = await this.client.get(`/download/${jobId}`, {
      responseType: 'arraybuffer'
    });
    return Buffer.from(response.data);
  }

  async renderAndWait(options, timeout = 300000) {
    const jobId = await this.renderAsync(options);
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const status = await this.getStatus(jobId);
      if (status.status === 'completed') {
        return await this.download(jobId);
      } else if (status.status === 'failed') {
        throw new Error(`Rendering failed: ${status.error}`);
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    throw new Error(`Job ${jobId} timed out`);
  }
}

// Usage
const client = new HTML2PDFClient('http://localhost:5000', 'your-api-key');

// Sync rendering
const pdf = await client.renderSync({
  html: '<h1>Report</h1>',
  format: 'A4'
});
fs.writeFileSync('report.pdf', pdf);

// Async rendering
const pdf2 = await client.renderAndWait({
  url: 'https://example.com',
  format: 'Letter'
});
fs.writeFileSync('webpage.pdf', pdf2);
```

## Configuration ⚙️

All settings are configured via environment variables. See `.env.example` for full list.

### Key Settings

```bash
# API Security
API_KEY_REQUIRED=True
API_KEYS=key1,key2,key3

# Limits (no artificial restrictions)
MAX_UPLOAD_SIZE_MB=100
SYNC_JOB_TIMEOUT_SEC=30
ASYNC_JOB_TIMEOUT_SEC=600

# Worker Concurrency
CELERY_WORKER_CONCURRENCY=4
CHROMIUM_POOL_SIZE=4

# Storage
STORAGE_TYPE=local  # or s3, gcs
STORAGE_PATH=/tmp/html2pdf
```

## Deployment 🚀

### Docker

```bash
# Build image
docker build -t html2pdf:latest .

# Run API
docker run -d -p 5000:5000 \
  -e API_KEYS=your-key \
  -e CELERY_BROKER_URL=redis://redis:6379/0 \
  html2pdf:latest

# Run worker
docker run -d \
  -e CELERY_BROKER_URL=redis://redis:6379/0 \
  html2pdf:latest \
  celery -A celery_worker.celery_app worker --loglevel=info
```

### Kubernetes

```bash
# Create namespace
kubectl apply -f deployment/kubernetes/namespace.yaml

# Create secret with your API keys
kubectl create secret generic html2pdf-secret \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=API_KEYS=your-key-1,your-key-2 \
  --namespace html2pdf

# Deploy Redis
kubectl apply -f deployment/kubernetes/redis.yaml

# Deploy ConfigMap
kubectl apply -f deployment/kubernetes/configmap.yaml

# Deploy API and Workers
kubectl apply -f deployment/kubernetes/api-deployment.yaml
kubectl apply -f deployment/kubernetes/worker-deployment.yaml

# Deploy Ingress (optional)
kubectl apply -f deployment/kubernetes/ingress.yaml

# Check status
kubectl get pods -n html2pdf
```

### AWS ECS

1. Build and push Docker image to ECR
2. Create ECS cluster with Fargate or EC2
3. Create task definitions for API and worker
4. Create ElastiCache Redis cluster
5. Create Application Load Balancer
6. Deploy services with auto-scaling

### Performance Tuning

```bash
# API Server
WORKERS=4  # Gunicorn workers
THREADS=2  # Threads per worker

# Celery Workers
CELERY_WORKER_CONCURRENCY=4  # Tasks per worker
CHROMIUM_POOL_SIZE=4  # Browser instances

# Resource Limits (Docker/K8s)
memory: 2Gi  # Per worker
cpu: 2000m   # Per worker
```

## Hosting & Deployment 🌐

Ready to deploy? Check out our deployment guides:

### ⚡ Quick Deploy (< 5 minutes)

**One-Click Deployment:**
- **[Render](https://render.com/deploy)** - Best free tier, auto-deploy from Git
- **[Railway](https://railway.app)** - Easiest setup, $5/month
- **[Fly.io](https://fly.io)** - Best value, great free tier

**Simple Command-Line:**
```bash
# Railway (3 minutes)
npm i -g @railway/cli && railway login && railway up

# Fly.io (5 minutes)
curl -L https://fly.io/install.sh | sh && fly launch

# DigitalOcean (10 minutes)
ssh root@your-droplet && curl -fsSL https://raw.githubusercontent.com/.../install-do.sh | bash
```

### 📚 Detailed Guides

- **[Quick Deploy Guide](./docs/QUICK_DEPLOY.md)** - Get started in 5 minutes
- **[Full Deployment Guide](./docs/DEPLOYMENT.md)** - Comprehensive guide for all platforms
- **[Platform Configs](.)** - Pre-configured files for each platform

### 💰 Cost Comparison

| Platform | Free Tier | Paid Plan | Best For |
|----------|-----------|-----------|----------|
| Fly.io | ✅ 3 VMs | $5-15/mo | Production |
| Render | ✅ Limited | $7-25/mo | Startups |
| Railway | ✅ Trial | $5-20/mo | Quick Start |
| DigitalOcean | ❌ | $12+/mo | Control |
| AWS ECS | ✅ 12mo | $20+/mo | Enterprise |

### 🔧 DIY VPS Setup

Got a VPS? Deploy with one command:

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/Pdfmaker-python/main/scripts/install-do.sh | bash
```

Includes: Docker, Docker Compose, auto-configuration, SSL setup

## Testing 🧪

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Skip slow tests

# Run specific test file
pytest tests/test_api.py
```

## Troubleshooting 🔧

### Common Issues

**Chromium crashes or timeouts:**
- Increase memory limits (2GB+ recommended)
- Reduce `CHROMIUM_POOL_SIZE`
- Increase `CHROMIUM_TIMEOUT_MS`
- Add `--no-sandbox` to `CHROMIUM_ARGS` (Docker)

**Rate limit errors:**
- Adjust `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_HOUR`
- Use multiple API keys for higher limits

**Large PDFs fail:**
- Increase `ASYNC_JOB_TIMEOUT_SEC`
- Use async endpoint instead of sync
- Enable streaming for very large HTMLs

**SSRF concerns:**
- Set `URL_DENYLIST` to block internal IPs
- Set `URL_ALLOWLIST` for strict control
- Enable `NETWORK_ISOLATION` for HTML rendering

## Architecture 🏗️

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  Flask API   │─────▶│   Redis     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      ▲
                            │                      │
                            ▼                      │
                     ┌──────────────┐             │
                     │    Celery    │─────────────┘
                     │   Workers    │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Playwright  │
                     │   Chromium   │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Storage    │
                     │ (Local/S3/GCS)│
                     └──────────────┘
```

## Security 🔒

- API key authentication
- Rate limiting (per-minute and per-hour)
- SSRF protection (URL allowlist/denylist)
- HTML sanitization (removes scripts/iframes)
- Network isolation option
- Secure secrets management
- No arbitrary code execution

## License 📄

MIT License - see LICENSE file

## Support 💬

- Issues: [GitHub Issues](https://github.com/yourusername/html2pdf/issues)
- Docs: See `/docs` directory
- Email: support@yourcompany.com

## Contributing 🤝

Pull requests welcome! Please:
1. Add tests for new features
2. Update documentation
3. Follow existing code style
4. Sign commits

---

Built with ❤️ using Flask, Playwright, and Celery
