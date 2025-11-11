# Production Deployment Quick Start - Ornina Avatar System

## 🚀 Deploy to 184.174.37.148 in 3 Steps

### Step 1: Prepare Production Server

```bash
# SSH into 184.174.37.148
ssh root@184.174.37.148

# Navigate to application directory
cd /var/www/avatar
```

### Step 2: Copy Production Configuration

```bash
# Use the production environment file
cp .env.production .env

# Verify configuration
cat .env | head -20
```

### Step 3: Deploy All Services

```bash
# Build production images (first time only)
docker-compose -f docker-compose.prod.yml build --no-cache

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Wait 30 seconds for startup
sleep 30

# Verify all services are healthy
docker-compose -f docker-compose.prod.yml ps
```

## ✅ Verify Deployment

### Check Service Status

```bash
# Should see all 4 services as "healthy"
docker-compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME                IMAGE                          STATUS
avatar-backend      ornina-avatar-backend:latest   Up X minutes (healthy)
avatar-frontend     ornina-avatar-frontend:latest  Up X minutes (healthy)
avatar-callcenter   ornina-avatar-callcenter:latest Up X minutes (healthy)
avatar-redis        redis:7-alpine                 Up X minutes (healthy)
```

### Test Services

```bash
# Test Frontend (should return HTML)
curl -k https://184.174.37.148:3000/ | head -20

# Test Backend Health (should return 200)
curl -k https://184.174.37.148:8080/health

# Test CallCenter Health (should return 200)
curl -k https://184.174.37.148:8000/health
```

## 📊 Monitor Logs

```bash
# View frontend logs
docker-compose -f docker-compose.prod.yml logs frontend

# View backend logs
docker-compose -f docker-compose.prod.yml logs backend

# View callcenter logs
docker-compose -f docker-compose.prod.yml logs callcenter

# View Redis logs
docker-compose -f docker-compose.prod.yml logs redis

# View all logs in real-time
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Common Operations

### Restart a Service

```bash
# Restart frontend
docker-compose -f docker-compose.prod.yml restart frontend

# Restart callcenter
docker-compose -f docker-compose.prod.yml restart callcenter

# Restart all services
docker-compose -f docker-compose.prod.yml restart
```

### Stop All Services

```bash
docker-compose -f docker-compose.prod.yml down
```

### View Service Details

```bash
# Show running containers
docker-compose -f docker-compose.prod.yml ps

# Show resource usage
docker stats --no-stream

# Show image details
docker images | grep ornina
```

## 🌐 Access Points After Deployment

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | https://184.174.37.148:3000/ | Avatar Video App |
| **Backend** | https://184.174.37.148:8080 | LiveKit Agents API |
| **CallCenter** | https://184.174.37.148:8000 | Call Center API |
| **CallCenter Health** | https://184.174.37.148:8000/health | API Health Check |
| **Redis** | 184.174.37.148:6379 | Cache (internal only) |

## 📋 What Each Service Does

### Frontend (Port 3000)
- React-based video avatar interface
- Real-time communication with backend
- User-friendly call interface
- Supports multi-language (Arabic primary)

### Avatar Backend (Port 8080)
- LiveKit Agents server
- AI-powered avatar responses
- Tavus video persona integration
- Face recognition and visual processing

### CallCenter (Port 8000)
- IVR (Interactive Voice Response) system
- Call routing and queue management
- CRM integration
- Ticket management
- Audio handling

### Redis (Port 6379)
- Distributed cache
- Session management
- Knowledge base caching
- Internal use only

## ⚙️ Configuration Reference

### Environment File: `.env.production`

Key variables:
```bash
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA
OPENAI_API_KEY=sk-proj-...
NEXT_PUBLIC_API_URL=https://184.174.37.148:8080
```

### Docker Compose: `docker-compose.prod.yml`

Features:
- ✅ Multi-stage builds for optimization
- ✅ Production restart policies (`restart: always`)
- ✅ Health checks on all services
- ✅ Proper dependency management
- ✅ Log persistence volumes
- ✅ Bridge network isolation

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs --tail 50 service-name

# Rebuild image
docker-compose -f docker-compose.prod.yml build --no-cache service-name

# Restart service
docker-compose -f docker-compose.prod.yml restart service-name
```

### Connection Issues

```bash
# Check network
docker network ls
docker network inspect avatar-network

# Check port bindings
netstat -tulpn | grep 3000
netstat -tulpn | grep 8000
netstat -tulpn | grep 8080
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart all services to free memory
docker-compose -f docker-compose.prod.yml restart

# Check image sizes
docker images | grep ornina
```

## 📚 Production Best Practices

1. **Keep Environment Variables Secure**
   - Never commit `.env.production` to version control
   - Rotate API keys regularly
   - Use secrets management for credentials

2. **Monitor Logs**
   - Set up log aggregation (ELK stack, etc.)
   - Monitor for errors in production logs
   - Track API response times

3. **Health Checks**
   - All services have health check endpoints
   - Monitor health check failures
   - Set up alerts for service restarts

4. **Updates**
   - Test updates in development first
   - Use `--no-cache` when rebuilding images
   - Plan updates during low-traffic periods

5. **Backups**
   - Backup `.env.production` securely
   - Back up Redis data volume
   - Keep version history of compose files

## 🎯 Next Steps

1. **Deploy**: Follow steps 1-3 above
2. **Verify**: Run the verification commands
3. **Monitor**: Check logs regularly
4. **Optimize**: Monitor resource usage and adjust as needed
5. **Scale**: Add load balancing if needed for high traffic

---

**Ready to Deploy!** All services are tested and production-ready. ✓
