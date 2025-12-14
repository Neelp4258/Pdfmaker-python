# Deploying to Render.com - MEMORY REQUIREMENTS

## ⚠️ CRITICAL: Memory Requirements

**Chromium browser requires AT LEAST 2GB RAM to work properly!**

If you see this error:
```
Web Service Pdfmaker-python exceeded its memory limit
```

Your instance **does not have enough RAM**.

## Render.com Plans & Memory

| Plan | RAM | Status | Cost |
|------|-----|--------|------|
| **Free** | 512MB | ❌ **TOO LOW** - Will crash! | $0 |
| **Starter** | 512MB | ❌ **TOO LOW** - Will crash! | $7/month |
| **Standard** | 2GB | ✅ **MINIMUM** - Works | $25/month |
| **Pro** | 4GB+ | ✅ **RECOMMENDED** - Best performance | $85/month |

## Solutions

### Option 1: Upgrade Render Plan (RECOMMENDED) ✅

**Steps:**
1. Go to your Render dashboard
2. Select your `html2pdf-api` service
3. Click "Settings" → "Instance Type"
4. Change from `Starter` to **`Standard`** (2GB RAM minimum)
5. Do the same for `html2pdf-worker` service
6. Click "Save Changes"

**Cost:** ~$25/month per service (2 services = ~$50/month total)

**Benefits:**
- ✅ Reliable PDF generation
- ✅ Handles large files with many images
- ✅ No crashes or memory errors
- ✅ Production-ready

---

### Option 2: Use Free Hosting with More RAM 🆓

If you can't afford Render's Standard plan, try these alternatives:

#### A) **Fly.io** (Generous Free Tier)
- **Free tier:** 3 VMs with 256MB RAM each = 768MB total
- **Paid:** 1GB RAM for $5/month (cheaper than Render)
- [Deploy Guide](https://fly.io/docs/speedrun/)

#### B) **Railway** (Free Trial)
- **Trial:** $5 free credit
- **Paid:** 1GB RAM for $5-10/month
- [Deploy Guide](https://railway.app)

#### C) **DigitalOcean App Platform**
- **Basic:** 1GB RAM for $12/month
- More affordable than Render Standard
- [Deploy Guide](https://www.digitalocean.com/products/app-platform)

#### D) **Your Own VPS** (Best Value)
- **DigitalOcean Droplet:** 2GB RAM for $12/month
- **Linode:** 2GB RAM for $12/month
- **Vultr:** 2GB RAM for $10/month
- Full control, best price-to-performance

---

### Option 3: Memory Optimization (Limited) ⚙️

If you must stay on Render Starter/Free tier, try these optimizations:

**Add to your Render environment variables:**

```bash
CHROMIUM_POOL_SIZE=1           # Only 1 browser instance (slower but less memory)
PAGE_LOAD_STRATEGY=domcontentloaded  # Don't wait for images (faster, less memory)
CHROMIUM_TIMEOUT_MS=30000      # Reduce timeout
CELERY_WORKER_CONCURRENCY=1    # Only 1 worker at a time
```

**Limitations:**
- ⚠️ Images may not load (domcontentloaded doesn't wait for images)
- ⚠️ Only 1 request at a time (very slow)
- ⚠️ May still crash with very large files
- ⚠️ Not reliable for production

**This is NOT recommended - it defeats the purpose of the image loading fix!**

---

## Why Your Puppeteer Works Locally

Your local computer/terminal has **8GB+ RAM**, so Chromium runs fine. Render's starter tier only has **512MB RAM** - **16x less** than your computer!

## Comparison Table

| Environment | RAM Available | Chromium Status | Large Files + Images |
|-------------|---------------|-----------------|---------------------|
| **Your Computer** | 8GB+ | ✅ Works perfectly | ✅ Works |
| **Render Starter** | 512MB | ❌ OUT OF MEMORY | ❌ Crashes |
| **Render Standard** | 2GB | ✅ Works | ✅ Works |
| **Render Pro** | 4GB+ | ✅ Works great | ✅ Works great |

## Recommended Action

### For Testing/Development:
1. **Deploy to Fly.io free tier** (more RAM than Render free)
2. Or **run locally** until ready for production

### For Production:
1. **Upgrade to Render Standard** ($25/month) - simplest solution
2. Or **use DigitalOcean VPS** ($12/month) - best value
3. Or **Railway/Fly.io paid tier** ($5-10/month) - cheaper alternative

## How to Deploy with Updated Config

I've already updated `render.yaml` with:
- ✅ `plan: standard` (2GB RAM)
- ✅ `CHROMIUM_POOL_SIZE=1` (memory optimized)
- ✅ Reduced worker concurrency
- ✅ Proper timeout settings

**To deploy with new config:**

```bash
# Commit the updated render.yaml
git add render.yaml
git commit -m "Update Render config for memory requirements"
git push

# Then in Render dashboard:
1. Go to your service settings
2. Change instance type to "Standard"
3. Redeploy
```

## Summary

**Question:** Is this solvable?
**Answer:** **YES!** But you need more RAM.

**Best Solutions (in order):**
1. ✅ **Upgrade to Render Standard** ($25/month) - Easy, reliable
2. ✅ **Switch to DigitalOcean VPS** ($12/month) - Best value
3. ✅ **Use Fly.io/Railway** ($5-10/month) - Cheaper alternative
4. ⚠️ **Memory optimization** (Free) - Very limited, not recommended

**The features you want (dark themes, hosted images, large files) require RAM. There's no way around it - Chromium is memory-intensive.**
