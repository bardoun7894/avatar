# Docker Environment Variables - Best Practices

## What Changed

### Before (Old Approach)
```dockerfile
# Setting empty defaults in Dockerfile
ENV LIVEKIT_URL=""
ENV LIVEKIT_API_KEY=""
ENV LIVEKIT_API_SECRET=""
ENV OPENAI_API_KEY=""
ENV DATABASE_URL=""
```

**Problems:**
- ❌ Hardcoded empty values in image
- ❌ Credentials not truly from environment
- ❌ Less flexible for different environments
- ❌ Harder to track what's actually needed

### After (New Approach - Direct from .env)
```dockerfile
# Only set infrastructure-level variables
ENV PYTHONUNBUFFERED=1

# Everything else comes from docker-compose.yml
# - env_file: ./callCenter/.env
# - environment: LIVEKIT_URL, OPENAI_API_KEY, DATABASE_URL, etc.
```

**Benefits:**
- ✅ Cleaner Dockerfile
- ✅ Credentials loaded directly from .env files
- ✅ More secure (no hardcoding)
- ✅ Better separation of concerns
- ✅ Easy to change per environment

---

## How It Works

### 1. Environment Variables Flow

```
Your Files                Docker Container
├─ .env.example          →  Environment
├─ avatary/.env          →  (env_file)
├─ callCenter/.env       →  Environment
└─ frontend/.env.local   →  Variables
```

### 2. Loading Methods (in priority order)

**Priority 1: docker-compose.yml environment section** (Highest)
```yaml
callcenter:
  environment:
    - LIVEKIT_URL=${LIVEKIT_URL}  # From root .env
    - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**Priority 2: docker-compose.yml env_file section**
```yaml
callcenter:
  env_file:
    - ./callCenter/.env  # All vars in this file loaded
```

**Priority 3: Dockerfile ENV** (Lowest)
```dockerfile
ENV PYTHONUNBUFFERED=1
```

### 3. Example Flow

```
callCenter/.env
├─ SUPABASE_URL=https://...
├─ DATABASE_URL=postgresql://...
└─ OPENAI_API_KEY=sk-...
     ↓
docker-compose.yml env_file
     ↓
Container starts
     ↓
Python app reads: os.environ.get('DATABASE_URL')
```

---

## Using in Your Python Code

### Reading Environment Variables

**Standard approach:**
```python
import os

# Get variable (required)
database_url = os.environ['DATABASE_URL']

# Get variable with default
debug_mode = os.environ.get('DEBUG', 'False')

# Get variable with error handling
try:
    api_key = os.environ['OPENAI_API_KEY']
except KeyError:
    print("ERROR: OPENAI_API_KEY not set!")
    raise
```

### Using with Python-dotenv (Optional)

```python
from dotenv import load_dotenv
import os

# Load .env file (useful for local development)
load_dotenv()

# Now you can read variables
database_url = os.environ.get('DATABASE_URL')
```

### Using with Pydantic (Recommended for FastAPI)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    livekit_url: str
    log_level: str = "INFO"  # Default value

    class Config:
        env_file = ".env"  # For local development

# Usage
settings = Settings()
print(settings.database_url)
```

---

## Environment Variable Rules

### Naming Conventions

```
PYTHONUNBUFFERED=1              # Infrastructure
LIVEKIT_URL=wss://...           # Service endpoints
LIVEKIT_API_KEY=...             # Credentials
DATABASE_URL=postgresql://...   # Connections
OPENAI_API_KEY=sk-...           # API keys
LOG_LEVEL=INFO                  # Configuration
NEXT_PUBLIC_API_URL=...         # Frontend public (React)
```

**Best Practices:**
- ✅ UPPERCASE with UNDERSCORES
- ✅ NEXT_PUBLIC_ prefix for frontend-visible vars
- ✅ Service-specific prefixes (AVATAR_, CALLCENTER_)
- ✅ Descriptive names (DATABASE_URL not DB_URL)

### Sensitive Variables

```yaml
# Don't expose via environment
OPENAI_API_KEY=...              # ✅ Secret
SUPABASE_KEY=...                # ✅ Secret
DATABASE_PASSWORD=...           # ✅ Secret

# Can be in environment
LIVEKIT_URL=...                 # ✅ Public endpoint
DATABASE_HOST=...               # ✅ Public address
LOG_LEVEL=...                   # ✅ Configuration
```

---

## Docker-Compose Configuration

### Method 1: Load from .env file (Current)

```yaml
services:
  callcenter:
    env_file:
      - ./callCenter/.env  # Load all variables from file
```

**What happens:**
```
callCenter/.env:
SUPABASE_URL=https://...
DATABASE_URL=postgresql://...

→ Container receives all variables
```

### Method 2: Explicit environment section

```yaml
services:
  callcenter:
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}      # From root .env
      - OPENAI_API_KEY=${OPENAI_API_KEY}  # From root .env
```

### Method 3: Combine both (Recommended)

```yaml
services:
  callcenter:
    env_file:
      - ./callCenter/.env               # Service-specific vars
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}     # Shared vars from root .env
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

## .env File Structure

### Root .env (Shared)
```bash
# /var/www/avatar/.env
LIVEKIT_URL=wss://livkit.example.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=sk-...
```

### Service-specific .env
```bash
# avatary/.env
TAVUS_API_KEY=...
TAVUS_PERSONA_ID=...
ELEVENLABS_API_KEY=...

# callCenter/.env
SUPABASE_URL=...
SUPABASE_KEY=...
DATABASE_URL=postgresql://...
DATABASE_HOST=...
DATABASE_USER=...
DATABASE_PASSWORD=...
```

---

## Testing Environment Variables

### Check Variables in Container

```bash
# List all environment variables
docker exec avatar-callcenter env

# Check specific variable
docker exec avatar-callcenter printenv DATABASE_URL

# Search for pattern
docker exec avatar-backend env | grep OPENAI
```

### Test from Host

```bash
# Before starting container
source callCenter/.env
echo $DATABASE_URL

# Verify file format
cat callCenter/.env | grep -v "^#" | grep -v "^$"
```

### Verify in Application

```python
import os

# Print all loaded variables
print("Loaded Environment Variables:")
for key in ['DATABASE_URL', 'OPENAI_API_KEY', 'LIVEKIT_URL']:
    value = os.environ.get(key, 'NOT SET')
    # Don't print actual secrets in logs!
    masked = value[:5] + '***' if value != 'NOT SET' else 'NOT SET'
    print(f"  {key}: {masked}")
```

---

## Common Issues & Solutions

### Issue: Variable not found in container

**Problem:**
```
KeyError: OPENAI_API_KEY
```

**Solution:**
```bash
# 1. Verify .env file exists and has content
cat callCenter/.env | grep OPENAI_API_KEY

# 2. Check docker-compose references the file
grep -A5 "env_file" docker-compose.yml

# 3. Check container received the variable
docker exec avatar-callcenter printenv OPENAI_API_KEY

# 4. Rebuild without cache
docker-compose build --no-cache callcenter
```

### Issue: Wrong value being used

**Problem:**
```
Database connection to wrong server
```

**Solution:**
```bash
# Check which file is being loaded
docker-compose config | grep -A10 "env_file"

# Verify file content
cat callCenter/.env | grep DATABASE

# Check container has correct value
docker exec avatar-callcenter printenv DATABASE_URL

# If wrong, update .env and restart
docker-compose restart callcenter
```

### Issue: Empty string instead of value

**Problem:**
```
ENV DATABASE_URL=""  # Old way - WRONG
```

**Solution:**
```dockerfile
# Don't set empty defaults in Dockerfile
# Let docker-compose provide the values
```

### Issue: Variable conflicts

**Problem:**
```
Same variable in .env and docker-compose
```

**Solution:**
```
docker-compose.yml environment section takes priority
├─ Highest: docker-compose environment
├─ Middle: docker-compose env_file
└─ Lowest: Dockerfile ENV
```

---

## Migration Guide

### Old Dockerfile
```dockerfile
ENV OPENAI_API_KEY=""
ENV DATABASE_URL=""
ENV LIVEKIT_URL=""
```

### New Dockerfile
```dockerfile
ENV PYTHONUNBUFFERED=1
# ^ Only infrastructure variables
# Everything else from docker-compose.yml
```

### docker-compose.yml
```yaml
services:
  callcenter:
    env_file:
      - ./callCenter/.env  # Load all vars
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}  # Shared vars
```

### .env file
```bash
# Root .env or callCenter/.env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
LIVEKIT_URL=wss://...
```

---

## Summary

### Environment Loading Order
1. **docker-compose.yml environment section** (highest priority)
2. **docker-compose.yml env_file section**
3. **Dockerfile ENV** (lowest priority)

### Best Practices
- ✅ Remove empty defaults from Dockerfile
- ✅ Use .env files for credential management
- ✅ Use docker-compose.yml env_file for loading
- ✅ Keep sensitive data out of Dockerfile
- ✅ Use meaningful variable names
- ✅ Document required variables

### Updated Files
- ✅ callCenter/Dockerfile - Cleaned up
- ✅ avatary/Dockerfile - Cleaned up
- ✅ docker-compose.yml - Already configured
- ✅ .env files - Have your credentials

---

**Your Setup Is Already Optimized!**

Your project is now using the best practices:
- Dockerfiles have minimal ENV settings
- docker-compose.yml loads from .env files
- All credentials stay in .env (not in git)
- Environment variables flow directly to containers

No further changes needed! 🎉
