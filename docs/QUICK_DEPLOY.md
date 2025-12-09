# ⚡ Quick Deploy Guide

Get HTML2PDF running in production in under 10 minutes!

---

## 🚀 Option 1: Railway (EASIEST - 3 minutes)

**Perfect for: Quick start, hobby projects**

### One-Command Deploy:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
cd Pdfmaker-python
railway up

# Set your API key
railway variables set API_KEYS=your-secret-key

# Done! Get your URL
railway domain
```

**Cost:** ~$5/month | **Free Trial:** $5 credit

---

## 🎨 Option 2: Render (BEST FREE TIER - 5 minutes)

**Perfect for: Testing, demos, MVP**

### One-Click Deploy:

1. Fork this repo on GitHub
2. Go to [render.com](https://render.com)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub
5. Select this repo
6. Click **"Apply"**

**Done!** Your service will be at `https://html2pdf-xxx.onrender.com`

**Cost:** Free (with limitations) or $7/month

---

## ✈️ Option 3: Fly.io (BEST VALUE - 5 minutes)

**Perfect for: Production, global edge deployment**

### Quick Deploy:

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (follow prompts)
cd Pdfmaker-python
fly launch

# Set secrets
fly secrets set API_KEYS=your-secret-key
fly secrets set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
fly deploy

# Done!
fly open
```

**Cost:** FREE for 3 VMs! Then ~$5/month

---

## 💧 Option 4: DigitalOcean (MOST CONTROL - 10 minutes)

**Perfect for: Production, full control**

### Quick Deploy Script:

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Run this script
curl -fsSL https://raw.githubusercontent.com/yourusername/Pdfmaker-python/main/scripts/install-do.sh | bash

# Set your domain
./setup-domain.sh yourdomain.com
```

**Cost:** $12/month (2GB RAM droplet)

---

## 🌐 Option 5: Vercel (FRONTEND ONLY)

**Note:** Vercel is great for the UI, but you'll need a separate backend.

1. Deploy API to Railway/Render/Fly
2. Deploy UI to Vercel (points to API)

```bash
npm i -g vercel
cd Pdfmaker-python
vercel deploy
```

---

## ⚙️ Environment Variables (Required)

Set these on ANY platform:

```bash
API_KEY_REQUIRED=True
API_KEYS=your-secret-key-here
SECRET_KEY=random-32-char-string
REDIS_URL=redis://...  # Usually auto-configured
```

Optional but recommended:

```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
MAX_UPLOAD_SIZE_MB=100
STORAGE_TYPE=local
```

---

## 🔑 Generate Secure Keys

```bash
# API Key
openssl rand -hex 16

# Secret Key
openssl rand -hex 32
```

---

## ✅ Verify Deployment

After deploying, test with:

```bash
# Health check
curl https://your-app-url.com/health

# Test PDF generation
curl -X POST https://your-app-url.com/render-sync \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Test</h1>", "format": "A4"}' \
  --output test.pdf

# Check if PDF was created
file test.pdf
```

---

## 🆘 Troubleshooting

### Service won't start?
```bash
# Check logs
railway logs  # Railway
fly logs      # Fly.io
heroku logs --tail  # Heroku
```

### Chromium crashes?
```bash
# Increase memory (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2G
```

### Can't access the UI?
- Make sure port 5000 is exposed
- Check firewall settings
- Verify the service is running

---

## 📊 Compare Deployment Options

| Feature | Railway | Render | Fly.io | DigitalOcean |
|---------|---------|--------|--------|--------------|
| Setup Time | 3 min | 5 min | 5 min | 10 min |
| Free Tier | $5 credit | Yes | Yes (3 VMs) | No |
| Auto HTTPS | ✅ | ✅ | ✅ | Manual |
| Auto Scale | ✅ | ✅ | ✅ | Manual |
| Redis Included | ✅ | ✅ | Add-on | Manual |
| Cost/Month | $5-20 | $7-25 | $0-15 | $12+ |
| Best For | Quick start | Free tier | Production | Control |

---

## 🎯 My Recommendations

### First Time / Testing?
→ **Render** (best free tier, easiest)

### Want to Deploy Fast?
→ **Railway** (3 minutes, dead simple)

### Going to Production?
→ **Fly.io** (great free tier, scales well)

### Need Full Control?
→ **DigitalOcean** (your own VPS)

---

## 🔥 Pro Tips

1. **Start with free tiers** - Test before committing
2. **Use managed Redis** - Don't host yourself
3. **Enable auto-scaling** - Handle traffic spikes
4. **Set up monitoring** - Use Sentry or similar
5. **Backup your config** - Save .env somewhere safe
6. **Use strong API keys** - Generate random ones
7. **Set up custom domain** - Looks more professional
8. **Enable HTTPS** - Most platforms do this automatically
9. **Monitor costs** - Set up billing alerts
10. **Test locally first** - Use docker-compose

---

## 📞 Need Help?

- **Issues?** Check logs first
- **Stuck?** Read the full [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Questions?** Open a GitHub issue

---

**Now go deploy and make some PDFs!** 🚀
