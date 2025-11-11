# Docker Deployment Guide - Call Center Audio Pipeline

**Status**: Ready for production deployment
**Docker Compose**: Already configured
**Call Center Service**: `avatar-callcenter` (port 8000)

---

## Overview

Your call center has been set up with Docker from the start. The `docker-compose.yml` already includes the call center service with all necessary configuration.

### Current Docker Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Network                      │
│              (avatar-network bridge)                 │
│                                                      │
│  ┌──────────────────┐    ┌──────────────────┐      │
│  │  Frontend        │    │  Avatar Backend  │      │
│  │  (Next.js)       │    │  (Python/Video)  │      │
│  │  Port: 3000      │    │  Port: 8080      │      │
│  └──────────────────┘    └──────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  CALL CENTER (FastAPI + LiveKit Agent)   │      │
│  │  🎙️  Audio Pipeline - Just Fixed!       │      │
│  │  Port: 8000                             │      │
│  │  Services:                               │      │
│  │  ✅ API Server (FastAPI)                │      │
│  │  ✅ LiveKit Agent Worker                │      │
│  │  ✅ Audio Orchestrator (NEW)            │      │
│  │  ✅ Supabase Persistence (NEW)          │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────┐                              │
│  │  Redis Cache     │                              │
│  │  Port: 6379      │                              │
│  └──────────────────┘                              │
│                                                      │
└─────────────────────────────────────────────────────┘
         ↓
    External Services
    - OpenAI (GPT-4, Whisper, TTS)
    - Supabase (PostgreSQL)
    - LiveKit (WebRTC Audio)
```

---

## Pre-Deployment Checklist

### ✅ What's Already Done

- [x] Dockerfile created and optimized
- [x] docker-compose.yml configured with all services
- [x] Call center service configured to run both API + Agent
- [x] Health checks configured
- [x] Network setup with bridge
- [x] Volume mounts for logs and persistence
- [x] Environment variable loading from .env files

### ✅ New Audio Pipeline Features

- [x] AudioOrchestrator (NEW) - Implemented and tested
- [x] LiveKit room operations - Implemented and tested
- [x] Supabase persistence - Implemented and tested
- [x] Fixed SDK imports - Implemented and tested

---

## 3-Step Docker Deployment

### Step 1: Configure Environment

**File**: `/var/www/avatar/callCenter/.env`

Ensure these values are set:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_URL=https://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...

# Supabase Configuration
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...

# Application Settings
DEFAULT_LANGUAGE=ar
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### Step 2: Create Database Tables

In Supabase SQL editor, run:

```sql
-- Customers table
CREATE TABLE IF NOT EXISTS customers (
  customer_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  email TEXT,
  tier TEXT DEFAULT 'starter',
  vip BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_interaction TIMESTAMP,
  total_calls INTEGER DEFAULT 0,
  total_tickets INTEGER DEFAULT 0
);

-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
  ticket_id TEXT PRIMARY KEY,
  customer_phone TEXT REFERENCES customers(phone),
  customer_name TEXT NOT NULL,
  customer_email TEXT,
  subject TEXT NOT NULL,
  description TEXT,
  department TEXT,
  priority TEXT,
  status TEXT,
  call_id TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Ticket history (audit trail)
CREATE TABLE IF NOT EXISTS ticket_history (
  id SERIAL PRIMARY KEY,
  ticket_id TEXT REFERENCES tickets(ticket_id),
  old_status TEXT,
  new_status TEXT,
  changed_by TEXT,
  reason TEXT,
  changed_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_tickets_customer_phone ON tickets(customer_phone);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
```

### Step 3: Build and Run

```bash
# Navigate to project root
cd /var/www/avatar

# Build call center image (with all fixes)
docker-compose build callcenter

# Start all services (or just callcenter)
docker-compose up -d

# Or start just call center
docker-compose up -d callcenter

# View logs
docker-compose logs -f callcenter

# Check health
docker-compose ps
```

---

## What the Docker Container Does

### Dockerfile Overview

**Image**: `python:3.11-slim`
**Workdir**: `/app`

### Components Running in Container

1. **FastAPI Server** (port 8000)
   - Handles HTTP requests
   - Manages token generation
   - Provides REST API endpoints
   - Started by supervisor

2. **LiveKit Agent Worker**
   - Connects to LiveKit server
   - Handles audio conversations
   - Runs STT/LLM/TTS pipeline
   - Started by supervisor

### Supervisor Configuration

Both services managed by supervisord:

```ini
[program:api]
command=python api.py

[program:agent]
command=python call_center_agent.py
```

### Health Checks

```bash
# Checks every 30s
curl http://localhost:8000/health

# If fails 3 times, marks unhealthy
# Waits 40s before first check
```

---

## Production Deployment

### For Production (docker-compose.prod.yml)

```bash
# Build with production settings
docker-compose -f docker-compose.prod.yml build callcenter

# Run with production config
docker-compose -f docker-compose.prod.yml up -d callcenter

# View logs
docker-compose -f docker-compose.prod.yml logs -f callcenter
```

### Production Checklist

- [ ] All environment variables set in `.env`
- [ ] Database tables created in Supabase
- [ ] HTTPS enabled for all external services
- [ ] SSL certificates configured
- [ ] Rate limiting enabled
- [ ] Error monitoring configured (Sentry)
- [ ] Logs aggregation configured
- [ ] Backups configured for Supabase
- [ ] Resource limits set (CPU, Memory)
- [ ] Auto-restart enabled

---

## Volume Mounts

### Current Configuration

```yaml
volumes:
  # Code (development only - comment for production)
  - ./callCenter:/app

  # Logs (persistent)
  - ./callCenter/logs:/app/logs

  # Virtual env (don't sync)
  - /app/venv
```

### For Production

Remove code mount (use Docker image instead):

```yaml
volumes:
  # Only keep logs and data
  - ./callCenter/logs:/app/logs
  # Add database volume if needed
  - callcenter-data:/app/data
```

---

## Docker Commands Reference

### Build

```bash
# Build call center image
docker-compose build callcenter

# Build with no cache (clean build)
docker-compose build --no-cache callcenter

# Build all services
docker-compose build
```

### Run

```bash
# Start call center
docker-compose up -d callcenter

# Start all services
docker-compose up -d

# Start with logs displayed
docker-compose up callcenter

# Start with specific env file
docker-compose --env-file .env.prod up -d callcenter
```

### Monitor

```bash
# View logs
docker-compose logs callcenter

# Follow logs (live)
docker-compose logs -f callcenter

# Last 100 lines
docker-compose logs --tail=100 callcenter

# Check service status
docker-compose ps

# Check specific container
docker inspect avatar-callcenter
```

### Stop/Restart

```bash
# Stop call center
docker-compose stop callcenter

# Stop all
docker-compose stop

# Restart call center
docker-compose restart callcenter

# Kill containers and remove volumes
docker-compose down -v
```

### Shell Access

```bash
# Enter container shell
docker-compose exec callcenter /bin/bash

# Run Python command
docker-compose exec callcenter python3 -c "import sys; print(sys.version)"

# Check installed packages
docker-compose exec callcenter pip list
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs callcenter

# Common issues:
# - Missing .env file → Create callCenter/.env
# - Missing OPENAI_API_KEY → Add to .env
# - Port 8000 in use → Change docker-compose.yml
# - LiveKit unavailable → Check LIVEKIT_URL
```

### Health Check Failing

```bash
# Check container is running
docker ps | grep callcenter

# Check if port is open
curl http://localhost:8000/health

# Check logs for errors
docker-compose logs callcenter | grep ERROR
```

### Audio Not Working

```bash
# Verify environment variables
docker-compose exec callcenter env | grep LIVEKIT
docker-compose exec callcenter env | grep OPENAI

# Check service dependencies
docker-compose exec callcenter curl -s http://localhost:8000/health

# Test OpenAI connection
docker-compose exec callcenter python3 -c "
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')
print('OpenAI API accessible')
"
```

### Database Connection Issues

```bash
# Check Supabase credentials
docker-compose exec callcenter env | grep SUPABASE

# Test connection
docker-compose exec callcenter python3 -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
client = create_client(url, key)
print('Supabase connected')
"
```

---

## Performance Tuning

### Resource Limits

Edit docker-compose.yml:

```yaml
callcenter:
  # ... existing config ...
  deploy:
    resources:
      limits:
        cpus: '2'          # 2 CPUs max
        memory: 2G         # 2GB RAM max
      reservations:
        cpus: '1'          # Reserve 1 CPU
        memory: 1G         # Reserve 1GB
```

### Scaling

For multiple call center instances:

```yaml
callcenter:
  deploy:
    replicas: 3              # 3 instances
  ports:
    - "8000-8002:8000"       # Port range
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Call Center

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker-compose build callcenter

      - name: Push to registry
        run: docker push your-registry/callcenter

      - name: Deploy
        run: docker-compose -f docker-compose.prod.yml up -d
```

---

## Monitoring & Observability

### Docker Stats

```bash
# Monitor resource usage
docker stats avatar-callcenter --no-stream

# Continuous monitoring
watch 'docker stats avatar-callcenter'
```

### Log Aggregation

To centralize logs:

```yaml
callcenter:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### Health Endpoint

The API provides a health check:

```bash
curl http://localhost:8000/health
# Returns: {"status": "ok"}
```

---

## Rollback

### To Previous Version

```bash
# Stop current container
docker-compose down callcenter

# Go back to previous commit
git checkout HEAD~1

# Rebuild and start
docker-compose build callcenter
docker-compose up -d callcenter
```

### Keep Multiple Versions

```bash
# Tag different versions
docker tag avatar-callcenter:latest avatar-callcenter:v1.0
docker tag avatar-callcenter:latest avatar-callcenter:v1.1

# Deploy specific version
docker-compose -f docker-compose.yml \
  -e SERVICE_VERSION=v1.0 \
  up -d callcenter
```

---

## Security Best Practices

### Never Commit Secrets

```bash
# .gitignore already includes:
.env
.env.local
.env.*.local
callCenter/.env
```

### Use Secret Management

For production, use Docker secrets:

```bash
# Create secret
echo "sk-proj-xxxxx" | docker secret create openai_key -

# Use in docker-compose
callcenter:
  secrets:
    - openai_key
  environment:
    OPENAI_API_KEY_FILE: /run/secrets/openai_key
```

### Network Isolation

Services communicate via Docker network (not host):

```yaml
networks:
  avatar-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## Next Steps

1. ✅ **Verify .env is configured** with all API keys
2. ✅ **Create database tables** in Supabase
3. ✅ **Build Docker image**: `docker-compose build callcenter`
4. ✅ **Start container**: `docker-compose up -d callcenter`
5. ✅ **Test audio**: Call http://localhost:3000/callcenter
6. ✅ **Monitor logs**: `docker-compose logs -f callcenter`
7. ✅ **Deploy to production** (see Production Deployment section)

---

## Support

### Helpful Commands

```bash
# Quick health check
docker-compose exec callcenter curl http://localhost:8000/health

# List running containers
docker-compose ps

# View environment
docker-compose config

# Validate compose file
docker-compose config --quiet

# Prune unused images
docker image prune -a

# Clean up everything (⚠️ WARNING)
docker-compose down -v
```

### Reference

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI**: https://fastapi.tiangolo.com/
- **LiveKit Agents**: https://docs.livekit.io/agents/

---

**Status**: ✅ Ready for production deployment via Docker
**Next**: Run `docker-compose build callcenter && docker-compose up -d callcenter`
