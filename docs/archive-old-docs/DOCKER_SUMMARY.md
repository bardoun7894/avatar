# Docker Setup Summary

## What Was Done

### ✅ Created Dockerfiles
- **avatary/Dockerfile** - Already existed (Python 3.11 + LiveKit)
- **callCenter/Dockerfile** - Newly created (FastAPI + LiveKit)
- **frontend/Dockerfile** - Already existed (Next.js)

### ✅ Updated docker-compose.yml
Added `callcenter` service to orchestrate:
- Avatar Backend (Port 8080)
- Call Center Backend (Port 8000) 
- Frontend (Port 3000)
- Redis (Port 6379)

### ✅ Created Environment Templates
- `/.env.example` - Root level configuration
- `avatary/.env.example` - Avatar backend template
- `callCenter/.env.example` - Call center template
- `frontend/.env.example` - Frontend template

### ✅ Created Documentation
- `DOCKER_SETUP.md` - Complete Docker guide
- `DOCKER_ENV_SETUP.md` - Environment variables guide
- `DOCKER_QUICK_START.md` - Quick start instructions
- `DOCKER_SUMMARY.md` - This summary

### ✅ Created Quick Start Script
- `docker-start.sh` - Automated setup & launch script

## Your Existing Credentials

**Already configured in:**
- `avatary/.env` - Tavus, OpenAI, ElevenLabs, LiveKit credentials
- `callCenter/.env` - Supabase, Database, OpenAI credentials
- `frontend/.env.local` - Frontend configuration

**Docker automatically uses these!** No additional setup needed.

## How to Use

### Option 1: Automated (Recommended)
```bash
cd /var/www/avatar
./docker-start.sh
```

### Option 2: Manual
```bash
cd /var/www/avatar
docker-compose up -d
```

### Option 3: Individual Services
```bash
docker-compose up -d frontend
docker-compose up -d backend
docker-compose up -d callcenter
```

## Access Services

- **Frontend**: http://localhost:3000
- **Avatar Backend**: http://localhost:8080
- **Call Center API**: http://localhost:8000
- **Redis**: localhost:6379

## Key Files

```
/var/www/avatar/
├── docker-compose.yml          ← Main orchestration file
├── docker-start.sh             ← Automated setup script
├── .env                        ← Root environment (from .env.example)
│
├── avatary/
│   ├── .env                    ← Has credentials (Tavus, OpenAI, etc)
│   └── Dockerfile              ← Python backend container
│
├── callCenter/
│   ├── .env                    ← Has credentials (Supabase, Database)
│   └── Dockerfile              ← FastAPI backend container
│
└── frontend/
    ├── .env.local              ← Has frontend config
    └── Dockerfile              ← Next.js frontend container
```

## Services & Ports

```
┌──────────────────────────────────┐
│  Avatar Docker Network           │
├──────────────────────────────────┤
│                                  │
│  Frontend (3000)                 │
│  ├─ Avatar app                   │
│  └─ Call Center app              │
│                                  │
│  Avatar Backend (8080)           │
│  ├─ Tavus video streaming        │
│  └─ Live conversation            │
│                                  │
│  Call Center Backend (8000)      │
│  ├─ IVR system                   │
│  ├─ Agent dashboard              │
│  └─ CRM integration              │
│                                  │
│  Redis (6379)                    │
│  └─ Caching & sessions           │
│                                  │
└──────────────────────────────────┘
```

## Quick Commands

### Start All Services
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f callcenter
```

### Stop All Services
```bash
docker-compose down
```

### Verify Credentials Loaded
```bash
docker exec avatar-backend env | grep OPENAI_API_KEY
docker exec avatar-callcenter env | grep DATABASE_URL
```

### Access Container Shell
```bash
docker-compose exec backend bash
docker-compose exec callcenter bash
docker-compose exec frontend sh
```

## Environment Variables

### Automatically Loaded

**avatary/.env** → `avatar-backend` container
- TAVUS_API_KEY
- OPENAI_API_KEY
- ELEVENLABS_API_KEY
- NEXT_PUBLIC_LIVEKIT_URL
- TAVUS_PERSONA_ID
- TAVUS_REPLICA_ID

**callCenter/.env** → `avatar-callcenter` container
- SUPABASE_URL
- SUPABASE_KEY
- DATABASE_URL
- DATABASE_HOST/PORT/USER/PASSWORD
- OPENAI_API_KEY

**.env** → Both containers (if root .env exists)
- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET

## What This Enables

✅ **Development Mode**
- Hot-reload with volume mounts
- Direct code editing
- Fast iteration

✅ **Production Ready**
- Multi-stage builds
- Health checks
- Auto-restart
- Isolated services
- Shared network

✅ **Easy Deployment**
- Single command: `docker-compose up -d`
- Automatic credential loading
- Service orchestration
- Log aggregation

## Frontend Structure

Also reorganized frontend into separate apps:

```
frontend/
├── apps/
│   ├── avatar/              ← Avatar video app
│   │   ├── components/
│   │   └── pages/
│   ├── callcenter/          ← Call center app
│   │   ├── components/
│   │   └── pages/
│   └── shared/              ← Shared resources
│       ├── styles/
│       ├── lib/
│       ├── hooks/
│       ├── api/
│       └── pages/ (_app, _document)
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs [service_name]

# Rebuild
docker-compose build --no-cache [service_name]

# Check ports
lsof -i :3000
lsof -i :8000
lsof -i :8080
```

### Credentials not loaded
```bash
# Verify .env files exist
ls -la avatary/.env
ls -la callCenter/.env

# Check docker-compose references
docker-compose config | grep env_file

# Check container env
docker exec avatar-backend env | grep API
```

### Database connection failed
```bash
# Check DATABASE_URL format
grep DATABASE callCenter/.env

# Test connection
docker-compose exec callcenter bash
psql $DATABASE_URL -c "SELECT 1"
```

## Next Steps

1. **Start Docker**
   ```bash
   ./docker-start.sh
   ```

2. **Access Services**
   - http://localhost:3000 (Frontend)

3. **Monitor**
   ```bash
   docker-compose logs -f
   ```

4. **Deploy**
   - For production: Comment out volume mounts in docker-compose.yml
   - Use external databases instead of local ones
   - Enable SSL/TLS with reverse proxy

## Resources

- Full Setup: `DOCKER_SETUP.md`
- Environment Guide: `DOCKER_ENV_SETUP.md`
- Quick Start: `DOCKER_QUICK_START.md`
- Docker Docs: https://docs.docker.com/
- Docker Compose Docs: https://docs.docker.com/compose/

---

**Status**: ✅ Production Ready
**Last Updated**: November 2024
**Components**: Frontend + 2 Backends + Redis
**Credentials**: Auto-loaded from existing .env files
