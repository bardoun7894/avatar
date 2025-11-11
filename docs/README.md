# Ornina Avatar System - Documentation

Complete documentation for the Ornina Avatar System, including deployment guides, system architecture, and troubleshooting.

## 📚 Quick Links

### Getting Started
- **[Deployment Quick Start](./DEPLOYMENT_QUICK_START.md)** - 3-step production deployment guide
- **[System Status](./SYSTEM_STATUS.md)** - Current system status and architecture overview

## 🏗️ System Architecture

The Ornina Avatar System is a multi-service architecture with four main components:

### Services Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│                   Port 3000 - React App                      │
│            Video Avatar Interface & User Dashboard           │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────────┐    ┌────────────▼──────────────┐
│  Avatar Backend      │    │  CallCenter Backend       │
│  (LiveKit Agents)    │    │  (FastAPI)                │
│  Port 8080           │    │  Port 8000                │
│  - AI Responses      │    │  - IVR System             │
│  - Face Recognition  │    │  - Call Routing           │
│  - Video Avatar      │    │  - CRM Integration        │
└───────┬──────────────┘    └────────────┬──────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
                ┌────────▼──────────┐
                │   Redis Cache     │
                │   Port 6379       │
                │   - Session Mgmt  │
                │   - Cache Layer   │
                └───────────────────┘
```

## 📋 Documentation Structure

### Deployment
- **[DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)**
  - Production deployment steps
  - Service verification
  - Monitoring and logging
  - Troubleshooting guide

### System Information
- **[SYSTEM_STATUS.md](./SYSTEM_STATUS.md)**
  - Current system health
  - Service architecture
  - Configuration reference
  - Known working features

## 🚀 Quick Start

### Local Development

```bash
# Start all services
cd /var/www/avatar
docker-compose up -d

# Verify services are healthy
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Deploy to 184.174.37.148
cd /var/www/avatar
cp .env.production .env
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

## 📊 Service Details

### Frontend (Port 3000)
- **Type**: Node.js + Next.js + React
- **Purpose**: Video avatar interface and user dashboard
- **Environment**: Build-time configuration
- **Status**: ✅ Healthy

### Avatar Backend (Port 8080)
- **Type**: Python + LiveKit Agents
- **Purpose**: AI-powered avatar responses and video streaming
- **Features**: Face recognition, Tavus integration, multi-language
- **Environment**: Runtime configuration
- **Status**: ✅ Healthy

### CallCenter (Port 8000)
- **Type**: Python + FastAPI
- **Purpose**: IVR system, call routing, and CRM integration
- **Features**: Call management, ticket system, audio handling
- **Environment**: Runtime configuration
- **Status**: ✅ Healthy

### Redis (Port 6379)
- **Type**: Redis (Alpine)
- **Purpose**: Distributed cache and session management
- **Status**: ✅ Healthy

## 🔧 Configuration

### Development Environment (`.env`)
Used for local development with localhost URLs.

Key variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
OPENAI_API_KEY=sk-proj-...
```

### Production Environment (`.env.production`)
Used for production deployment at IP 184.174.37.148.

Key variables:
```bash
NEXT_PUBLIC_API_URL=https://184.174.37.148:8080
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
OPENAI_API_KEY=sk-proj-...
```

## 📝 Common Operations

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f callcenter
```

### Restart Services
```bash
# Single service
docker-compose restart frontend

# All services
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

## 🐛 Troubleshooting

### Service Won't Start
1. Check logs: `docker-compose logs service-name`
2. Rebuild image: `docker-compose build --no-cache service-name`
3. Restart service: `docker-compose restart service-name`

### Connection Issues
1. Verify ports are open: `netstat -tulpn | grep PORT`
2. Check network: `docker network inspect avatar-network`
3. Test connectivity: `curl http://localhost:PORT/health`

### High Memory Usage
1. Check usage: `docker stats`
2. Restart services: `docker-compose restart`
3. Check image sizes: `docker images`

For detailed troubleshooting, see [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md#-troubleshooting)

## 🌐 Access Points

### Local (Development)
- Frontend: http://localhost:3000/
- Backend: http://localhost:8080
- CallCenter: http://localhost:8000

### Production (184.174.37.148)
- Frontend: https://184.174.37.148:3000/
- Backend: https://184.174.37.148:8080
- CallCenter: https://184.174.37.148:8000

## 📚 Additional Resources

### Docker Commands
```bash
# Build all images
docker-compose build

# Build specific image
docker-compose build frontend

# Remove unused images
docker image prune

# View image details
docker images | grep avatar
```

### Network Commands
```bash
# List networks
docker network ls

# Inspect network
docker network inspect avatar-network

# View network details
docker inspect container-name
```

### Database/Cache
```bash
# Connect to Redis CLI
docker exec -it avatar-redis redis-cli

# Check Redis memory
docker exec -it avatar-redis redis-cli INFO memory

# Flush cache
docker exec -it avatar-redis redis-cli FLUSHALL
```

## 🔐 Security Notes

1. **Keep credentials secure**
   - Never commit `.env.production` to version control
   - Rotate API keys regularly
   - Use secrets management in production

2. **Network Security**
   - Use HTTPS in production
   - Restrict port access with firewall rules
   - Monitor for unauthorized access

3. **Container Security**
   - Run containers as non-root users
   - Keep images updated
   - Scan for vulnerabilities

## 📞 Support

For issues or questions:

1. Check the [Troubleshooting](./DEPLOYMENT_QUICK_START.md#-troubleshooting) section
2. Review logs: `docker-compose logs service-name`
3. Check [System Status](./SYSTEM_STATUS.md) for current state
4. Verify configuration in `.env` or `.env.production`

## ✅ System Status

**Current Status**: ✅ HEALTHY & PRODUCTION READY

- ✅ Frontend: Healthy
- ✅ Backend: Healthy
- ✅ CallCenter: Healthy
- ✅ Redis: Healthy

All services are running and verified to be working correctly.

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
**Deployment Target**: 184.174.37.148:3000
