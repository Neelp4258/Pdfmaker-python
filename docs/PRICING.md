# 💰 Pricing Guide - HTML2PDF Service

Compare hosting costs and choose the best option for your needs.

---

## 📊 Monthly Cost Breakdown

### Free / Hobby Tier

| Platform | Free Tier | Limits | Best For |
|----------|-----------|--------|----------|
| **Fly.io** | ✅ FREE | 3 shared VMs, 160GB transfer | Testing, small apps |
| **Render** | ✅ FREE | Sleeps after 15min, 750hrs/mo | Demos, staging |
| **Railway** | ✅ $5 credit | Trial credits | Quick testing |
| **Google Cloud Run** | ✅ FREE | 2M requests/mo | Serverless testing |

**Recommendation:** Start with **Fly.io** - Best free tier with no sleep!

---

### Small Business ($10-30/month)

Perfect for: Side projects, small businesses, MVP

| Setup | Monthly Cost | Specs | Handles |
|-------|--------------|-------|---------|
| **Railway Starter** | $5-10 | 512MB-1GB RAM | 10-50 req/min |
| **Render Standard** | $7 | 512MB RAM | 10-50 req/min |
| **DigitalOcean Basic** | $12 + $7 Redis | 2GB RAM | 50-100 req/min |
| **Fly.io Shared** | $5-15 | 256MB per VM | 20-80 req/min |

**Recommendation:** **Railway** for ease, **DigitalOcean** for value

#### Cost Example: Railway
- API service: $5/mo (starter)
- Worker service: $5/mo (starter)
- Redis: $3/mo (512MB)
- **Total: ~$13/month**

---

### Medium Business ($30-60/month)

Perfect for: Growing apps, consistent traffic

| Setup | Monthly Cost | Specs | Handles |
|-------|--------------|-------|---------|
| **DigitalOcean Pro** | $24 + $15 Redis | 4GB RAM | 200+ req/min |
| **Railway Pro** | $20-40 | 2GB RAM per service | 100-200 req/min |
| **AWS ECS (t3.medium)** | $30 + $15 RDS | 4GB RAM, 2 vCPU | 300+ req/min |
| **Fly.io Dedicated** | $30-50 | 1GB per VM × 3 | 200+ req/min |

**Recommendation:** **DigitalOcean** - Best balance of cost and performance

#### Cost Example: DigitalOcean
- Droplet (4GB): $24/mo
- Managed Redis: $15/mo
- Backups: $5/mo
- **Total: ~$44/month**

---

### Production ($60-150/month)

Perfect for: Established apps, high traffic

| Setup | Monthly Cost | Specs | Handles |
|-------|--------------|-------|---------|
| **DigitalOcean HA** | $48 + $30 Redis | 8GB RAM, 4 vCPU | 500+ req/min |
| **AWS ECS Cluster** | $60-100 | t3.large × 2 | 1000+ req/min |
| **Google Cloud Run** | $50-100 | Auto-scale | Variable |
| **Azure Container** | $80-120 | 8GB RAM | 500+ req/min |

**Recommendation:** **AWS ECS** or **Cloud Run** for auto-scaling

#### Cost Example: AWS ECS
- t3.large instances × 2: $60/mo
- RDS (db.t3.small): $25/mo
- Application Load Balancer: $16/mo
- ElastiCache Redis: $15/mo
- Data transfer: $10/mo
- **Total: ~$126/month**

---

### Enterprise ($150+/month)

Perfect for: Large scale, mission-critical

| Setup | Monthly Cost | Specs | Features |
|-------|--------------|-------|----------|
| **AWS ECS + Auto Scaling** | $200-500 | Multi-AZ, HA | Global CDN |
| **Google Cloud Platform** | $180-400 | Multi-region | Auto-scale |
| **Azure Enterprise** | $250-600 | HA setup | SLA 99.99% |
| **Dedicated Servers** | $150-300 | Full control | Custom setup |

**Recommendation:** **AWS** or **GCP** with auto-scaling and multi-region

---

## 🧮 Cost Calculator

### Usage-Based Estimate

**Formula:** (API calls/month × average processing time × cost per hour)

#### Example 1: Small Blog
- 1,000 PDFs/month
- 2 seconds each
- Platform: Railway ($5/mo)
- **Cost: $5/month**

#### Example 2: Medium SaaS
- 50,000 PDFs/month
- 3 seconds each
- Platform: DigitalOcean ($24/mo)
- **Cost: $44/month**

#### Example 3: Large Platform
- 500,000 PDFs/month
- 4 seconds each
- Platform: AWS ECS Auto-scaling
- **Cost: $150-250/month**

---

## 💡 Cost Optimization Tips

### 1. Start Small, Scale Up
✅ Begin with free tier
✅ Monitor usage
✅ Upgrade when needed

### 2. Use Async Processing
✅ Queue large jobs
✅ Reduce immediate resource needs
✅ Better user experience

### 3. Implement Caching
✅ Cache common PDFs
✅ Use CDN for delivery
✅ Reduce rendering costs

### 4. Optimize Worker Concurrency
```yaml
# Start with 2 workers
CELERY_WORKER_CONCURRENCY=2

# Scale to 4 when needed
CELERY_WORKER_CONCURRENCY=4
```

### 5. Use Spot Instances (AWS)
✅ 50-70% cost savings
✅ Perfect for worker nodes
✅ Handle interruptions gracefully

### 6. Rightsize Your Resources
```yaml
# Don't over-provision
resources:
  limits:
    memory: 2G  # Not 8G if you don't need it
    cpu: 1      # Not 4
```

### 7. Clean Up Old PDFs
```bash
# Auto-delete PDFs after 24 hours
JOB_RESULT_TTL_SEC=86400
```

### 8. Use Reserved Instances (Long-term)
✅ 30-40% discount (AWS)
✅ Commit to 1-3 years
✅ Predictable workloads

---

## 📉 Cost Reduction Strategies

### Strategy 1: Hybrid Approach
- **API on serverless** (Cloud Run) - Pay per use
- **Workers on VPS** (DigitalOcean) - Fixed cost
- **Redis on managed service** - Reliability

**Savings:** 30-40%

### Strategy 2: Single VPS Everything
- One powerful droplet
- Run all services with docker-compose
- Manual management

**Savings:** 50-60%

### Strategy 3: Use Free Tiers Creatively
- Fly.io: 3 free VMs
- Upstash Redis: Free tier
- Cloudflare CDN: Free

**Savings:** 80-90% (with limits)

---

## 🎯 Recommended Setups by Budget

### $0/month - Just Testing
```
Platform: Fly.io (free tier)
Setup: 3 VMs, Upstash Redis
Limits: Light usage only
```

### $10/month - Hobby Project
```
Platform: Railway
Setup: 1 API + 1 Worker + Redis
Limits: ~1,000 PDFs/day
```

### $30/month - Small Business
```
Platform: DigitalOcean
Setup: 2GB Droplet + Managed Redis
Limits: ~5,000 PDFs/day
```

### $60/month - Growing Company
```
Platform: DigitalOcean or AWS
Setup: 4GB Droplet + Redis + Load Balancer
Limits: ~20,000 PDFs/day
```

### $150+/month - Scale
```
Platform: AWS ECS or GCP
Setup: Auto-scaling cluster
Limits: Unlimited with auto-scale
```

---

## 📞 Questions?

**"Which platform is cheapest?"**
→ Fly.io (free tier) or Hetzner VPS ($5/mo)

**"Which is best value?"**
→ DigitalOcean ($12/mo for 2GB droplet)

**"Which is easiest?"**
→ Railway ($5-10/mo, zero config)

**"Which scales best?"**
→ AWS ECS or Google Cloud Run (pay per use)

**"I have $10/month"**
→ Railway (managed) or Hetzner (DIY)

**"I have $50/month"**
→ DigitalOcean 4GB + Managed Redis

**"I need enterprise"**
→ AWS or GCP with auto-scaling

---

**Pro Tip:** Start with Railway or Fly.io free tier, test your usage, then move to DigitalOcean for production. Scale to AWS/GCP when you hit 100K+ PDFs/month.
