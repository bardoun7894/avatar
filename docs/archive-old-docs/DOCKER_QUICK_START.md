# Docker Quick Start - Using Your Existing Credentials

## TL;DR - Start in 2 Commands

```bash
cd /var/www/avatar
./docker-start.sh
```

That's it! Your existing credentials from `.env` files will be automatically loaded into Docker containers.

---

## How It Works

Your project already has credentials in these files:

### Existing Credential Files

1. **`avatary/.env`** - Contains:
   - ✅ Tavus API Key
   - ✅ OpenAI API Key
   - ✅ ElevenLabs API Key
   - ✅ LiveKit URL
   - ✅ Tavus Persona & Replica IDs

2. **`callCenter/.env`** - Contains:
   - ✅ Supabase URL & Keys
   - ✅ Database URL & Credentials
   - ✅ OpenAI API Key

3. **`frontend/.env.local`** - Contains:
   - ✅ Frontend configuration

## Automatic Credential Loading

The `docker-compose.yml` is already configured to load these files:

```yaml
services:
  backend:
    env_file:
      - ./avatary/.env           # ✅ Automatically loaded

  callcenter:
    env_file:
      - ./callCenter/.env        # ✅ Automatically loaded

  frontend:
    environment:
      - NEXT_PUBLIC_LIVEKIT_URL=${LIVEKIT_URL}  # From .env
```

**No additional setup needed!** Docker automatically uses your existing credentials.

---

## Quick Start Methods

### Method 1: Automated Script (Recommended)

```bash
cd /var/www/avatar
chmod +x docker-start.sh
./docker-start.sh
```

**What it does:**
- ✅ Checks Docker installation
- ✅ Verifies .env files exist
- ✅ Checks for required credentials
- ✅ Builds Docker images
- ✅ Starts all services
- ✅ Displays service URLs and commands

### Method 2: Manual Docker Commands

```bash
cd /var/www/avatar

# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Method 3: Start Specific Services

```bash
# Start only frontend
docker-compose up -d frontend

# Start only backend
docker-compose up -d backend

# Start only call center
docker-compose up -d callcenter
```

---

## Access Your Services

After starting with Docker:

### Frontend
- **URL**: http://localhost:3000
- **Apps**: Avatar & Call Center

### Avatar Backend
- **Port**: 8080
- **Container**: `avatar-backend`

### Call Center Backend
- **Port**: 8000
- **Container**: `avatar-callcenter`
- **API**: http://localhost:8000

### Redis
- **Port**: 6379
- **Container**: `avatar-redis`

---

## Verify Credentials Are Loaded

### Check if credentials loaded in container

```bash
# View all environment variables
docker exec avatar-backend env | head -20

# Check specific API keys
docker exec avatar-backend printenv OPENAI_API_KEY
docker exec avatar-callcenter printenv DATABASE_URL

# Check Tavus configuration
docker exec avatar-backend env | grep TAVUS
```

### Check service logs

```bash
# Avatar backend initialization
docker-compose logs backend | grep -i "initialized\|connected\|tavus"

# Call center database connection
docker-compose logs callcenter | grep -i "database\|supabase\|connected"
```

---

## Common Commands

### View Live Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f callcenter

# Last 100 lines with timestamps
docker-compose logs -f --tail=100 --timestamps frontend
```

### Stop Services
```bash
# Stop without removing
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart callcenter
```

### Update Credentials
```bash
# Edit credential files
nano avatary/.env
nano callCenter/.env

# Restart services to pick up changes
docker-compose restart
```

### Access Container Shell
```bash
# Backend shell
docker-compose exec backend bash

# Call center shell
docker-compose exec callcenter bash

# Frontend shell
docker-compose exec frontend sh
```

### Check Container Resource Usage
```bash
docker stats
```

---

## Environment Variable Reference

### Automatically Loaded From Files

#### From `avatary/.env`
```
TAVUS_API_KEY=457fcf2b5d734c34bbb88c8f55c1de60
TAVUS_PERSONA_ID=pa9c7a69d551
TAVUS_REPLICA_ID=rca8a38779a8
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=nH7M8bGCLQbKoS0wBZj7
NEXT_PUBLIC_LIVEKIT_URL=wss://...
```

#### From `callCenter/.env`
```
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
DATABASE_URL=postgresql://...
DATABASE_HOST=...
DATABASE_USER=...
DATABASE_PASSWORD=...
```

**All these are automatically passed to containers!**

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 3000
lsof -i :3000

# Or use different port
docker-compose -f docker-compose.yml -e "FRONTEND_PORT=3001" up -d
```

### Container Exits Immediately

```bash
# Check logs for error
docker-compose logs callcenter

# Rebuild without cache
docker-compose build --no-cache callcenter

# Check if .env file is readable
cat callCenter/.env | head
```

### Credentials Not Loaded

```bash
# Verify env_file path in docker-compose.yml
docker-compose config | grep -A5 "env_file"

# Check if .env file exists and has content
ls -la avatary/.env
cat avatary/.env | grep API_KEY

# Verify file format (no extra spaces)
file avatary/.env
```

### Database Connection Issues

```bash
# Check database URL format
grep DATABASE_URL callCenter/.env

# Test connection from container
docker-compose exec callcenter bash
psql $DATABASE_URL -c "SELECT 1"
```

### LiveKit Connection Issues

```bash
# Check LiveKit URL
grep LIVEKIT avatary/.env
grep LIVEKIT_URL frontend/.env.local

# View connection logs
docker-compose logs backend | grep -i livekit
docker-compose logs frontend | grep -i livekit
```

---

## File Structure Used

```
/var/www/avatar/
├── .env                          # Root env (created from .example)
├── docker-compose.yml            # ✅ Already configured
├── docker-start.sh              # ✅ Quick start script
├── DOCKER_ENV_SETUP.md          # ✅ Detailed setup guide
├── DOCKER_QUICK_START.md        # ✅ This file
│
├── avatary/
│   ├── .env                     # ✅ Your credentials
│   ├── Dockerfile              # ✅ Already exists
│   └── ... (source code)
│
├── callCenter/
│   ├── .env                     # ✅ Your credentials
│   ├── Dockerfile              # ✅ Newly created
│   └── ... (source code)
│
└── frontend/
    ├── .env.local              # ✅ Your credentials
    ├── Dockerfile              # ✅ Already exists
    └── ... (source code)
```

---

## Security Notes

### Production Best Practices

1. **Never commit .env files**
   ```bash
   # Already in .gitignore (verify)
   cat .gitignore | grep ".env"
   ```

2. **Use Docker Secrets for production**
   ```bash
   echo "your_secret_here" | docker secret create api_key -
   ```

3. **Mask credentials in logs**
   ```bash
   # Use docker-compose secrets instead of env_file in production
   ```

4. **Rotate credentials regularly**
   - Update `.env` files
   - Restart services
   - Monitor logs for any issues

---

## Next Steps

### 1. Start Docker
```bash
./docker-start.sh
```

### 2. Access Services
- Frontend: http://localhost:3000
- Monitor: `docker-compose ps`
- Logs: `docker-compose logs -f`

### 3. Verify Everything Works
```bash
# Test frontend
curl http://localhost:3000

# Check container health
docker-compose ps

# View initialization logs
docker-compose logs backend | grep -i ready
```

### 4. Keep Services Running
```bash
# Run in background
docker-compose up -d

# Check status anytime
docker-compose ps

# Stop when done
docker-compose down
```

---

## Summary

✅ **Credentials**: Already in `avatary/.env` and `callCenter/.env`
✅ **Docker Setup**: Already configured in `docker-compose.yml`
✅ **Quick Start**: Run `./docker-start.sh`
✅ **Services**: Automatically load your credentials

**No manual credential setup needed!** Just run the script and Docker handles the rest.

---

**Questions?** Check `DOCKER_ENV_SETUP.md` for detailed information about environment variables.
