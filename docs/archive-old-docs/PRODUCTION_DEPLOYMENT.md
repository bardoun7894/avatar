# Ornina Avatar - Production Deployment Guide

**Status:** ✅ Ready for Production  
**Deployment URL:** https://184.174.37.148:3000/  
**Version:** 1.0.0  
**Last Updated:** 2025-11-10

---

## Quick Start

```bash
# 1. Copy production config
cp .env.production .env

# 2. Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify
docker-compose -f docker-compose.prod.yml ps
```

---

## Services

| Service | Port | Container | Image |
|---------|------|-----------|-------|
| Frontend | 3000 | avatar-frontend | ornina-avatar-frontend:latest |
| Backend | 8080 | avatar-backend | ornina-avatar-backend:latest |
| Call Center API | 8000 | avatar-callcenter | ornina-avatar-callcenter:latest |
| Redis Cache | 6379 | avatar-redis | redis:7-alpine |

---

## Access Production

- **Frontend:** https://184.174.37.148:3000/
- **Backend API:** https://184.174.37.148:8080
- **Call Center API:** https://184.174.37.148:8000

---

## Common Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f frontend

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restart specific service
docker-compose -f docker-compose.prod.yml restart frontend

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

---

## Environment Configuration

All credentials are configured in `.env.production`:
- ✅ LiveKit API credentials
- ✅ OpenAI API key
- ✅ Supabase database
- ✅ Tavus avatar service
- ✅ ElevenLabs voice service

---

## Production Checklist

- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Database backups enabled
- [ ] Monitoring configured
- [ ] Log rotation enabled
- [ ] Health checks verified

