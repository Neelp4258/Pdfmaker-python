# ⚡ QUICK FIX - Playwright Error Code 100

Got the "Installation process ended with code 100" error? Here's how to fix it in 30 seconds!

---

## 🚀 Option 1: Rebuild with Fixed Dockerfile (FASTEST!)

```bash
# Stop everything
docker-compose down

# Rebuild with the new fixed Dockerfile (no cache)
docker-compose build --no-cache

# Start services
docker-compose up -d

# Check if it's working
curl http://localhost:5000/health
```

**Done!** The new Dockerfile fixes all Playwright issues automatically! ✅

---

## 🔧 Option 2: Run the Fix Script (Local Development)

```bash
chmod +x scripts/fix-playwright.sh
./scripts/fix-playwright.sh
```

This will:
- Install all missing system dependencies
- Try multiple installation methods
- Handle ARM/M1 Mac issues automatically

---

## 🍎 Option 3: For Mac M1/M2/M3 (Apple Silicon)

```bash
# Use the ARM-optimized Dockerfile
docker-compose down
docker build -f Dockerfile.arm -t html2pdf:latest .
docker-compose up -d
```

Or without Docker:
```bash
brew install chromium
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/homebrew/bin/chromium
python app.py
```

---

## 🐧 Option 4: Manual Fix (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 \
    libgtk-3-0 libgbm1 fonts-liberation

# Reinstall Playwright
pip install --force-reinstall playwright
playwright install chromium --with-deps
```

---

## ✅ Verify It's Fixed

```bash
# Test Playwright
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start(); print('✅ Works!')"

# Test PDF generation
curl -X POST http://localhost:5000/render-sync \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Test</h1>", "format": "A4"}' \
  --output test.pdf

file test.pdf
# Should say: PDF document
```

---

## 🆘 Still Not Working?

1. **Check Docker memory**: Increase to 4GB+ in Docker Desktop settings
2. **Try different Docker builder**:
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```
3. **Read full troubleshooting guide**: `docs/TROUBLESHOOTING.md`
4. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

---

**The rebuild (Option 1) fixes 99% of cases! Just do that first!** 🎯
