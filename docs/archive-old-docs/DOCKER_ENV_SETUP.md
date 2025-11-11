# Using Existing Credentials with Docker

Your project already has environment credentials configured. Here's how to use them with Docker.

## Current Setup

You have `.env` files in:
- `/avatary/.env` - Avatar backend credentials
- `/callCenter/.env` - Call Center backend credentials
- `/frontend/.env.local` - Frontend configuration

## How Docker Uses Environment Variables

The `docker-compose.yml` file references `.env` files in two ways:

### 1. Service-Level `env_file`

```yaml
services:
  backend:
    env_file:
      - ./avatary/.env        # Loads all variables from this file

  callcenter:
    env_file:
      - ./callCenter/.env     # Loads all variables from this file
```

This automatically loads all variables from the `.env` files into the containers.

### 2. Root-Level `.env` File

Create `/var/www/avatar/.env` (root project level) for shared variables:

```bash
cp /var/www/avatar/.env.example /var/www/avatar/.env
```

This file is used for variables like:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`

## Setup Steps

### Step 1: Verify Existing .env Files

Check that all `.env` files exist:

```bash
# Check avatary
cat /var/www/avatar/avatary/.env

# Check callCenter
cat /var/www/avatar/callCenter/.env

# Check frontend
cat /var/www/avatar/frontend/.env.local
```

### Step 2: Create Root .env (if missing)

```bash
cd /var/www/avatar

# Create from example
cp .env.example .env

# Or extract values from existing files:
cat avatary/.env | grep LIVEKIT >> .env
cat avatary/.env | grep OPENAI >> .env
cat callCenter/.env | grep SUPABASE >> .env
```

### Step 3: Verify Variables Are Used

The docker-compose.yml already references these files:

```yaml
services:
  backend:
    env_file:
      - ./avatary/.env          ✅ Loaded automatically

  callcenter:
    env_file:
      - ./callCenter/.env       ✅ Loaded automatically

  frontend:
    environment:
      - NEXT_PUBLIC_LIVEKIT_URL=${LIVEKIT_URL}  # From root .env
```

### Step 4: Start Docker with Your Credentials

```bash
cd /var/www/avatar

# Start all services (they will load your .env files)
docker-compose up -d

# Verify services started with correct credentials
docker-compose logs backend | grep -i "livekit\|tavus\|openai"
docker-compose logs callcenter | grep -i "supabase\|database\|openai"
```

## What Gets Loaded Into Each Container

### Avatar Backend (avatary)
From `./avatary/.env`:
```
✅ TAVUS_API_KEY
✅ TAVUS_PERSONA_ID
✅ TAVUS_REPLICA_ID
✅ OPENAI_API_KEY
✅ ELEVENLABS_API_KEY
✅ ELEVENLABS_VOICE_ID
✅ NEXT_PUBLIC_LIVEKIT_URL
```

### Call Center Backend
From `./callCenter/.env`:
```
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ SUPABASE_ANON_KEY
✅ DATABASE_URL
✅ DATABASE_HOST
✅ DATABASE_PORT
✅ DATABASE_NAME
✅ DATABASE_USER
✅ DATABASE_PASSWORD
✅ OPENAI_API_KEY (if present)
```

### Frontend
From `./frontend/.env.local` or root `.env`:
```
✅ NEXT_PUBLIC_LIVEKIT_URL
✅ NEXT_PUBLIC_API_URL
```

## Environment Variable Precedence

Docker uses credentials in this order:

1. **Root level `.env`** - Variables defined here
   ```
   /var/www/avatar/.env
   ```

2. **Service-level `env_file`** - Variables from service .env files
   ```
   ./avatary/.env
   ./callCenter/.env
   ```

3. **Explicit `environment` section** - Overrides above
   ```yaml
   environment:
     - PYTHONUNBUFFERED=1
     - LOG_LEVEL=INFO
   ```

**Example**: If `OPENAI_API_KEY` exists in both root and `avatary/.env`, the root value takes precedence.

## How to Use with Docker

### Option 1: Automatic Loading (Recommended)

Your `.env` files are already configured in docker-compose.yml:

```bash
docker-compose up -d
# Credentials automatically loaded from .env files
```

### Option 2: Override at Runtime

```bash
# Override specific variable
docker-compose -e OPENAI_API_KEY=new_key up -d

# Or set before running
export OPENAI_API_KEY=new_key
docker-compose up -d
```

### Option 3: Use Environment File in Docker Run

```bash
docker run --env-file ./avatary/.env avatar:backend
```

## Verify Credentials Are Loaded

### Check Container Environment

```bash
# See all variables in a container
docker exec avatar-backend env | grep -i "tavus\|openai\|livekit"

# Check specific variable
docker exec avatar-backend printenv OPENAI_API_KEY

# Check all variables (careful with secrets!)
docker exec avatar-callcenter env
```

### Check Logs for Successful Initialization

```bash
# Avatar Backend
docker-compose logs backend | grep -i "initialized\|connected\|ready"

# Call Center Backend
docker-compose logs callcenter | grep -i "initialized\|connected\|database"

# Check for errors
docker-compose logs backend | grep -i "error\|failed"
```

## Common Issues & Solutions

### Issue: Container can't find credentials

**Problem**: `ERROR: Environment variable not found`

**Solution**:
```bash
# Verify .env file exists
ls -la ./avatary/.env
ls -la ./callCenter/.env

# Check file has proper format
cat ./avatary/.env | head

# Rebuild container
docker-compose build --no-cache backend
docker-compose up -d
```

### Issue: Wrong credentials being used

**Problem**: Container uses different API key than expected

**Solution**:
```bash
# Check which file is being loaded
docker-compose config | grep -A5 "env_file"

# Verify environment variables in container
docker exec avatar-backend env | grep API_KEY

# Check root .env isn't conflicting
cat .env | grep -i key
```

### Issue: Secrets exposed in logs

**Problem**: Sensitive data visible in docker logs

**Solution**:
```bash
# Don't log entire env (filter in docker-compose.yml)
# Or use Docker secrets for production
# Or use environment variable masking
```

## Best Practices

### 1. Keep .env Secure
```bash
# Add to .gitignore (should already be done)
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo "avatary/.env" >> .gitignore
echo "callCenter/.env" >> .gitignore

# Don't commit actual credentials
git status | grep ".env"  # Should show nothing
```

### 2. Use .env.example for Templates
```bash
# Keep examples without actual values
git add .env.example
git add avatary/.env.example
git add callCenter/.env.example
git add frontend/.env.example

# But don't commit actual .env files
git add -f .env  # Will be rejected by .gitignore
```

### 3. For Production

Use Docker Secrets instead:

```bash
# Create secret
echo "sk-proj-xxxxx" | docker secret create openai_key -

# In docker-compose.yml (production)
secrets:
  openai_key:
    external: true

services:
  backend:
    secrets:
      - openai_key
```

### 4. Environment Variable Naming

Follow conventions:
```
PRODUCTION: UPPERCASE_WITH_UNDERSCORES
Service prefix: AVATAR_, CALLCENTER_
Secrets: API_KEY, API_SECRET, PASSWORD
Public: NEXT_PUBLIC_* (for frontend)
```

## Quick Reference

### Start with Your Credentials
```bash
cd /var/www/avatar
docker-compose up -d
```

### Check What's Loaded
```bash
docker exec avatar-backend env
docker exec avatar-callcenter env
```

### Update Credentials
```bash
# Edit .env files
nano .env
nano avatary/.env
nano callCenter/.env

# Restart services
docker-compose restart backend callcenter
```

### Reset to Fresh Start
```bash
# Remove all containers
docker-compose down

# Verify .env files have correct values
cat avatary/.env
cat callCenter/.env

# Start fresh
docker-compose up -d
```

## Summary

Your credentials are already in place:

✅ `avatary/.env` - Has Tavus, OpenAI, LiveKit credentials
✅ `callCenter/.env` - Has Supabase, Database, OpenAI credentials
✅ Docker-compose.yml - Already configured to load these files

**To use with Docker:**
1. Create root `.env` if needed: `cp .env.example .env`
2. Run `docker-compose up -d`
3. Credentials automatically loaded from service `.env` files
4. Verify with `docker exec` commands above

That's it! Your existing credentials will be used in Docker containers automatically.
