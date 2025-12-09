# 🚀 Deployment Guide - HTML2PDF Service

Complete guide for deploying HTML2PDF to production with various hosting providers.

---

## 📊 Quick Comparison

| Platform | Cost | Difficulty | Best For | Free Tier |
|----------|------|------------|----------|-----------|
| **Railway** | ~$5-20/mo | ⭐ Easy | Hobby/Small | Yes (Limited) |
| **Render** | ~$7-25/mo | ⭐⭐ Easy | Startups | Yes (Limited) |
| **Fly.io** | ~$5-15/mo | ⭐⭐ Medium | Edge Computing | Yes (Good) |
| **DigitalOcean** | $12-50/mo | ⭐⭐⭐ Medium | Full Control | No |
| **AWS ECS** | ~$20-100/mo | ⭐⭐⭐⭐ Hard | Enterprise | Yes (12 months) |
| **Google Cloud Run** | Pay-per-use | ⭐⭐⭐ Medium | Scalable | Yes (Good) |
| **Azure Container** | ~$30-80/mo | ⭐⭐⭐⭐ Hard | Enterprise | Yes (12 months) |
| **Heroku** | ~$7-50/mo | ⭐ Easy | Quick Start | No |
| **VPS (Linode/Vultr)** | $5-40/mo | ⭐⭐⭐ Medium | Custom Setup | No |

---

## 🎯 RECOMMENDED: Railway (Easiest!)

**Perfect for:** Getting started, hobby projects, small businesses
**Cost:** ~$5-10/month
**Pros:** One-click deploy, automatic HTTPS, built-in Redis, easy scaling
**Cons:** Can get expensive at scale

### Step-by-Step Railway Deployment

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
# or
curl -fsSL https://railway.app/install.sh | sh
```

2. **Login:**
```bash
railway login
```

3. **Initialize Project:**
```bash
cd Pdfmaker-python
railway init
```

4. **Add Services:**
```bash
# Deploy the app
railway up

# Add Redis
railway add
# Select "Redis" from the list
```

5. **Set Environment Variables:**
```bash
railway variables set API_KEY_REQUIRED=True
railway variables set API_KEYS=your-key-1,your-key-2
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

6. **Deploy:**
```bash
railway up
```

7. **Get Your URL:**
```bash
railway domain
```

**Done!** Your service is live at `https://your-app.up.railway.app` 🎉

---

## 🔥 Render (Great Free Tier!)

**Perfect for:** Testing, personal projects, MVP
**Cost:** Free tier available, then $7+/month
**Pros:** Great free tier, easy to use, automatic deploys from Git
**Cons:** Free tier sleeps after 15min inactivity

### Step-by-Step Render Deployment

1. **Create `render.yaml` in your repo** (already included in project):
```yaml
services:
  - type: web
    name: html2pdf-api
    env: docker
    plan: starter
    envVars:
      - key: API_KEY_REQUIRED
        value: true
      - key: API_KEYS
        generateValue: true
      - key: SECRET_KEY
        generateValue: true
      - key: REDIS_URL
        fromService:
          type: redis
          name: html2pdf-redis
          property: connectionString

  - type: redis
    name: html2pdf-redis
    plan: starter
    maxmemoryPolicy: allkeys-lru

  - type: worker
    name: html2pdf-worker
    env: docker
    plan: starter
    dockerCommand: celery -A celery_worker.celery_app worker --loglevel=info
```

2. **Deploy:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Select branch
   - Click "Apply"

3. **Get Your URL:**
   - Your service will be at `https://html2pdf-api.onrender.com`

**Free Tier Notes:**
- Service sleeps after 15min inactivity
- Takes ~30s to wake up
- Perfect for testing/demos!

---

## 🌐 Fly.io (Best Free Tier!)

**Perfect for:** Global distribution, edge computing
**Cost:** Generous free tier (3 VMs), then ~$5/month
**Pros:** Great free tier, global edge network, fast
**Cons:** More complex setup

### Step-by-Step Fly.io Deployment

1. **Install Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login:**
```bash
fly auth login
```

3. **Launch App:**
```bash
cd Pdfmaker-python
fly launch --no-deploy

# Answer prompts:
# App name: html2pdf
# Region: Choose closest to you
# Would you like to set up a PostgreSQL database? No
# Would you like to set up an Upstash Redis database? Yes
```

4. **Create `fly.toml`** (if not auto-generated):
```toml
app = "html2pdf"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "5000"
  FLASK_ENV = "production"
  API_KEY_REQUIRED = "True"

[[services]]
  http_checks = []
  internal_port = 5000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_gb = 1
```

5. **Set Secrets:**
```bash
fly secrets set API_KEYS=your-key-1,your-key-2
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
```

6. **Deploy:**
```bash
fly deploy
```

7. **Scale Workers (Optional):**
```bash
# Add Celery workers
fly scale count 2
```

8. **Open Your App:**
```bash
fly open
```

**Free Tier Includes:**
- 3 shared-cpu VMs
- 160GB outbound data transfer
- Upstash Redis included

---

## 💧 DigitalOcean (Best VPS Option)

**Perfect for:** Full control, production apps, predictable pricing
**Cost:** $12/month (2GB Droplet) + $7/month (Managed Redis)
**Pros:** Simple, reliable, great docs, predictable pricing
**Cons:** Manual setup required

### Step-by-Step DigitalOcean Deployment

1. **Create Droplet:**
   - Go to [DigitalOcean](https://digitalocean.com)
   - Create → Droplets
   - Choose: Ubuntu 22.04 LTS
   - Plan: Basic ($12/mo - 2GB RAM)
   - Add SSH key

2. **SSH into Droplet:**
```bash
ssh root@your-droplet-ip
```

3. **Install Docker:**
```bash
apt update
apt install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker
```

4. **Clone & Deploy:**
```bash
cd /opt
git clone https://github.com/yourusername/Pdfmaker-python.git
cd Pdfmaker-python

# Create .env file
cp .env.example .env
nano .env  # Edit with your settings

# Start services
docker-compose up -d
```

5. **Setup Nginx (Optional but recommended):**
```bash
apt install -y nginx certbot python3-certbot-nginx

# Create nginx config
cat > /etc/nginx/sites-available/html2pdf << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;
    }
}
EOF

ln -s /etc/nginx/sites-available/html2pdf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

6. **Get SSL Certificate:**
```bash
certbot --nginx -d your-domain.com
```

7. **Setup Auto-restart:**
```bash
cat > /etc/systemd/system/html2pdf.service << 'EOF'
[Unit]
Description=HTML2PDF Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/Pdfmaker-python
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl enable html2pdf
systemctl start html2pdf
```

**Done!** Your service is live at `https://your-domain.com`

---

## ☁️ Google Cloud Run (Serverless!)

**Perfect for:** Pay-per-use, automatic scaling, zero maintenance
**Cost:** ~$0.30-5/month (free tier: 2 million requests/month)
**Pros:** True serverless, only pay for what you use, auto-scaling
**Cons:** Cold starts, Redis needs separate hosting

### Step-by-Step Cloud Run Deployment

1. **Install gcloud CLI:**
```bash
# Install from https://cloud.google.com/sdk/docs/install
gcloud init
```

2. **Build & Push Container:**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable services
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and push
cd Pdfmaker-python
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/html2pdf

# Deploy
gcloud run deploy html2pdf \
  --image gcr.io/YOUR_PROJECT_ID/html2pdf \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --set-env-vars "API_KEY_REQUIRED=True,API_KEYS=your-key" \
  --set-env-vars "SECRET_KEY=$(openssl rand -hex 32)"
```

3. **Setup Redis (Memorystore):**
```bash
gcloud redis instances create html2pdf-redis \
  --size=1 \
  --region=us-central1 \
  --tier=basic

# Get Redis IP
gcloud redis instances describe html2pdf-redis --region=us-central1
```

4. **Update Cloud Run with Redis URL:**
```bash
gcloud run services update html2pdf \
  --set-env-vars "REDIS_URL=redis://REDIS_IP:6379/0"
```

**Free Tier Includes:**
- 2 million requests/month
- 360,000 GB-seconds
- 180,000 vCPU-seconds

---

## 🐳 AWS ECS (Enterprise Grade)

**Perfect for:** Large scale, enterprise, AWS ecosystem
**Cost:** ~$20-100/month (t3.medium: ~$30/mo + ECS)
**Pros:** Highly scalable, AWS integration, battle-tested
**Cons:** Complex setup, expensive, steep learning curve

### Quick AWS ECS Setup

1. **Use AWS Copilot CLI:**
```bash
# Install Copilot
curl -Lo /usr/local/bin/copilot https://github.com/aws/copilot-cli/releases/latest/download/copilot-linux
chmod +x /usr/local/bin/copilot

# Initialize
cd Pdfmaker-python
copilot init

# Answer prompts:
# Application name: html2pdf
# Service type: Load Balanced Web Service
# Service name: api
# Dockerfile: ./Dockerfile

# Deploy
copilot deploy
```

2. **Add Redis:**
```bash
copilot storage init
# Choose: Redis cluster
```

3. **Add Workers:**
```bash
copilot svc init
# Service name: worker
# Service type: Backend Service
```

**Done!** AWS Copilot handles everything!

---

## 🔧 VPS Options (Full Control)

### Linode / Vultr / Hetzner

**Cost:** $5-40/month
**Pros:** Cheapest, full control, predictable
**Cons:** Manual everything, you maintain it

#### Recommended Specs:
- **Small:** 2GB RAM, 1 CPU - $10-12/mo (handles 10-50 req/min)
- **Medium:** 4GB RAM, 2 CPU - $20-24/mo (handles 100+ req/min)
- **Large:** 8GB RAM, 4 CPU - $40-48/mo (handles 500+ req/min)

#### Deploy with Docker:
```bash
# Same as DigitalOcean steps above
```

---

## 🎯 My Recommendation Based on Use Case

### Just Starting / Testing
**→ Fly.io or Render**
- Great free tiers
- Easy setup
- Perfect for MVP

### Small Business / Production
**→ Railway or DigitalOcean**
- Railway: If you want easy management
- DigitalOcean: If you want control + value

### High Traffic / Enterprise
**→ AWS ECS or Google Cloud Run**
- Auto-scaling
- High reliability
- Pay for what you use

### Tight Budget
**→ Hetzner VPS ($5/mo)**
- Cheapest option
- Great specs for price
- Located in Europe

---

## 🔐 Production Checklist

Before going live, make sure:

- [ ] Set strong `SECRET_KEY`
- [ ] Enable `API_KEY_REQUIRED=True`
- [ ] Set up proper API keys
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups
- [ ] Set up domain name
- [ ] Enable rate limiting
- [ ] Configure proper CORS
- [ ] Set up logging
- [ ] Test with load testing tool
- [ ] Set up health checks
- [ ] Configure auto-restart
- [ ] Set resource limits
- [ ] Enable security headers

---

## 📈 Scaling Tips

### Horizontal Scaling
```bash
# Add more workers
docker-compose up -d --scale worker=4

# Kubernetes
kubectl scale deployment html2pdf-worker --replicas=5
```

### Vertical Scaling
```yaml
# docker-compose.yml
services:
  worker:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Redis Optimization
```bash
# In Redis
maxmemory 2gb
maxmemory-policy allkeys-lru
```

---

## 🆘 Troubleshooting

### Chromium Crashes
```bash
# Add to docker-compose.yml
environment:
  - CHROMIUM_ARGS=--no-sandbox,--disable-setuid-sandbox
deploy:
  resources:
    limits:
      memory: 2G  # Increase memory
```

### Out of Memory
```bash
# Reduce worker concurrency
- CELERY_WORKER_CONCURRENCY=2
- CHROMIUM_POOL_SIZE=2
```

### Slow PDF Generation
```bash
# Scale workers
docker-compose up -d --scale worker=3

# Or increase resources
```

---

## 💰 Cost Breakdown (Monthly)

### Hobby Project (~$5-10/mo)
- Fly.io: 3 free VMs
- Railway: $5 starter
- Render: $7 starter

### Small Business (~$20-30/mo)
- DigitalOcean: $12 droplet + $7 Redis
- Railway: $20 with scaling
- AWS: t3.small + RDS

### Production (~$50-100/mo)
- AWS ECS: t3.medium + RDS + ELB
- GCP: Cloud Run + Memorystore
- DigitalOcean: $40 droplet + managed Redis

### Enterprise (~$200+/mo)
- AWS: Multiple instances + Auto Scaling
- GCP: Multi-region Cloud Run
- Azure: Container Instances + load balancing

---

**Need help choosing?** DM me what your budget and expected traffic is! 🚀
