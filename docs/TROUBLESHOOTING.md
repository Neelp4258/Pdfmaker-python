# 🔧 Troubleshooting Guide

Common issues and solutions for HTML2PDF service.

---

## 🚨 Playwright Installation Error (Code 100)

### Problem
```
Error: Installation process ended with code 100
playwright install chromium failed
```

### Root Causes
1. **Missing system dependencies** - Chromium needs specific OS libraries
2. **Permission issues** - Can't write to browser cache directory
3. **Network issues** - Can't download Chromium binary
4. **Architecture mismatch** - ARM vs x86 compatibility
5. **Disk space** - Not enough space for browser download (~300MB)

---

## ✅ Solutions

### Quick Fix #1: Use the Fix Script

```bash
cd Pdfmaker-python
chmod +x scripts/fix-playwright.sh
./scripts/fix-playwright.sh
```

This script will:
- Detect your OS and architecture
- Install missing system dependencies
- Try multiple installation methods
- Provide ARM/M1 Mac specific fixes

---

### Quick Fix #2: Rebuild with New Dockerfile

The updated Dockerfile fixes all common issues:

```bash
# Stop and remove old containers
docker-compose down

# Rebuild from scratch
docker-compose build --no-cache

# Start services
docker-compose up -d
```

---

### Quick Fix #3: Manual System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libatspi2.0-0 libxshmfence1 fonts-liberation

# Then install Playwright
playwright install chromium --with-deps
```

#### macOS:
```bash
# Install via Homebrew (easiest)
brew install chromium

# Set environment variable
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/homebrew/bin/chromium

# Or install Playwright normally
playwright install chromium
```

#### RHEL/CentOS/Fedora:
```bash
sudo yum install -y \
    nss nspr atk at-spi2-atk cups-libs \
    libdrm libXcomposite libXdamage libXrandr \
    mesa-libgbm pango cairo alsa-lib liberation-fonts

playwright install chromium
```

---

### Quick Fix #4: For ARM/Apple Silicon (M1/M2/M3)

Use the ARM-optimized Dockerfile:

```bash
# Build with ARM Dockerfile
docker build -f Dockerfile.arm -t html2pdf:arm .

# Or update docker-compose.yml to use Dockerfile.arm
# Then:
docker-compose up -d
```

Or use system Chromium:

```bash
# Install via Homebrew
brew install chromium

# Set environment variable
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/homebrew/bin/chromium

# Run without Docker
python app.py
```

---

### Quick Fix #5: Skip Chromium Download (Use System Browser)

If you have Chromium installed system-wide:

```bash
# Find Chromium location
which chromium || which chromium-browser || which google-chrome

# Set environment variable (example path)
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# Skip Playwright download
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Install Playwright without browsers
pip install playwright
playwright install-deps chromium  # Only install system deps
```

---

## 🐳 Docker-Specific Issues

### Issue: Docker build fails at Playwright step

**Solution 1: Use BuildKit**
```bash
DOCKER_BUILDKIT=1 docker-compose build
```

**Solution 2: Increase Docker memory**
```bash
# Docker Desktop: Settings → Resources → Memory (increase to 4GB+)
```

**Solution 3: Build with no cache**
```bash
docker-compose build --no-cache
```

**Solution 4: Multi-stage build issue**
```bash
# Build specific stage
docker build --target dependencies -t html2pdf:deps .
docker build --target application -t html2pdf:app .
```

---

### Issue: Permission denied in Docker

**Solution:**
```dockerfile
# In Dockerfile, run as root (already done in updated Dockerfile)
# Don't switch to non-root user for Playwright

# Or give permissions:
RUN chmod -R 777 /ms-playwright
```

---

### Issue: Chromium crashes in Docker

**Solution: Add more shared memory**

Update `docker-compose.yml`:
```yaml
services:
  api:
    shm_size: '2gb'  # Add this
    environment:
      - CHROMIUM_ARGS=--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage
```

Or run with:
```bash
docker run --shm-size=2g html2pdf
```

---

## 🌐 Platform-Specific Issues

### Render.com

**Issue:** Build fails on Render

**Solution:** Render uses Docker, so use the updated Dockerfile
```yaml
# render.yaml already configured correctly
# Just rebuild on Render dashboard
```

---

### Railway

**Issue:** Playwright installation timeout

**Solution:** Increase build timeout
```toml
# railway.toml
[build]
  buildCommand = "pip install -r requirements.txt && playwright install chromium --with-deps"

[deploy]
  startCommand = "gunicorn --bind 0.0.0.0:$PORT app:app"
  healthcheckPath = "/health"
  healthcheckTimeout = 100
```

---

### Fly.io

**Issue:** ARM architecture issues

**Solution:** Use Dockerfile.arm or specify architecture
```toml
# fly.toml
[build]
  dockerfile = "Dockerfile.arm"
```

---

### Heroku

**Issue:** Buildpack doesn't support Playwright

**Solution:** Use Docker instead
```yaml
# heroku.yml
build:
  docker:
    web: Dockerfile
```

---

## 💾 Local Development Issues

### Issue: Playwright works in Docker but not locally

**Solution:**

1. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get install -y $(playwright show-dependencies chromium)

# macOS
brew install chromium
```

2. **Reinstall Playwright:**
```bash
pip uninstall playwright
pip install playwright
playwright install chromium --with-deps
```

3. **Check Python version:**
```bash
python --version  # Should be 3.8+
```

---

### Issue: "Browser executable not found"

**Solution:**

```bash
# Find where Playwright stores browsers
python -c "from playwright.sync_api import sync_playwright; print(sync_playwright().start().chromium.executable_path)"

# Or set manually
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
playwright install chromium
```

---

## 🔍 Debugging Commands

### Check Playwright installation:
```bash
playwright --version
playwright show-dependencies chromium
```

### Test Chromium launch:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    print("✅ Chromium launched successfully!")
    browser.close()
```

### Check system dependencies:
```bash
# Ubuntu/Debian
dpkg -l | grep -E 'libnss3|libxss1|libasound2'

# macOS
brew list | grep chromium
```

### Docker debug:
```bash
# Build and enter container
docker-compose build
docker-compose run --rm api bash

# Inside container, test Playwright
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()"
```

---

## 📊 Error Code Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 100 | Installation failed | Use fix script or install deps manually |
| 1 | Browser not found | Run `playwright install chromium` |
| 137 | Out of memory | Increase Docker memory or add `--shm-size=2g` |
| 127 | Command not found | Install Playwright: `pip install playwright` |
| Permission denied | No write access | Run as root or fix permissions |

---

## 🆘 Still Not Working?

### 1. Collect Debug Info
```bash
# System info
uname -a
python --version
playwright --version

# Docker info (if using Docker)
docker version
docker-compose version

# Playwright debug
PWDEBUG=1 playwright install chromium
```

### 2. Try Minimal Test
```bash
# Create test file
cat > test_playwright.py << 'EOF'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content("<h1>Test</h1>")
    pdf = page.pdf()
    print(f"✅ PDF generated: {len(pdf)} bytes")
    browser.close()
EOF

# Run test
python test_playwright.py
```

### 3. Alternative: Use Docker Pre-built Image
```bash
# Use official Playwright image as base
docker pull mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Modify Dockerfile:
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
# ... rest of your Dockerfile
```

### 4. Contact Support
- Open GitHub issue with error logs
- Include: OS, Python version, Docker version (if using)
- Include output of: `playwright install chromium --verbose`

---

## ✅ Verification

After fixing, verify everything works:

```bash
# Test API
curl -X POST http://localhost:5000/render-sync \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Test</h1>", "format": "A4"}' \
  --output test.pdf

# Check if PDF was created
file test.pdf
# Should output: test.pdf: PDF document, version 1.4
```

---

**Pro Tip:** The updated Dockerfile (committed in this fix) handles 99% of installation issues automatically. Just rebuild! 🚀
