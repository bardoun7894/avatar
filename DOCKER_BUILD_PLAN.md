# Docker Build & Test Plan for Voice Call Changes

**Date:** 2025-11-11
**Objective:** Build and test Docker images with voice call WebRTC streaming implementation
**Status:** Ready to Execute

---

## Overview

This document provides step-by-step instructions to build Docker images for the voice call implementation and test them locally.

### What Will Be Built

| Service | Changes | Status |
|---|---|---|
| **Frontend** | call-with-audio.tsx refactored | ✅ Ready |
| **Call Center Backend** | config.py updated | ✅ Ready |
| **Avatar Backend** | No changes needed | ✅ Ready |
| **Redis** | No changes | ✅ Ready |

---

## Part 1: Pre-Build Verification

### Step 1a: Check Docker Installation
```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 20.10+ (or higher)
Docker Compose version 2.x+ (or higher)
```

### Step 1b: Verify All Files Are in Place
```bash
# Check key files exist
ls -la /var/www/avatar/frontend/apps/callcenter/pages/call-with-audio.tsx
ls -la /var/www/avatar/callCenter/config.py
ls -la /var/www/avatar/.env.docker
ls -la /var/www/avatar/docker-compose.yml
```

Expected: All files should exist with recent modification dates

### Step 1c: Check Environment Variables
```bash
# Verify .env file has required variables
grep "LIVEKIT_URL" /var/www/avatar/.env.docker
grep "OPENAI_API_KEY" /var/www/avatar/callCenter/.env
grep "NEXT_PUBLIC_LIVEKIT_URL" /var/www/avatar/.env.docker
```

Expected: All variables should have values (not empty)

---

## Part 2: Build Images

### Step 2a: Build Frontend Image
```bash
cd /var/www/avatar

# Build the frontend with voice call changes
docker build \
  --build-arg NEXT_PUBLIC_LIVEKIT_URL="wss://tavus-agent-project-i82x78jc.livekit.cloud" \
  --build-arg NEXT_PUBLIC_API_URL="http://localhost:8000" \
  --build-arg NEXT_PUBLIC_CALLCENTER_LIVEKIT_URL="wss://tavus-agent-project-i82x78jc.livekit.cloud" \
  --build-arg NEXT_PUBLIC_SUPABASE_URL="https://uzzejiaxyvuhcfcvjyiv.supabase.co" \
  --build-arg NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6emVqaWF4eXZ1aGNmY3ZqeWl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NjUxOTEsImV4cCI6MjA3NjI0MTE5MX0.dnHU1HpwXsI5f7i-75K2qA9rnnzYpfjA6TqVfm3vOP0" \
  -f frontend/Dockerfile \
  -t avatar-frontend:voice-call \
  ./frontend
```

**Expected output:**
```
Successfully tagged avatar-frontend:voice-call
```

**What this does:**
- Installs npm dependencies
- Builds Next.js app with new call-with-audio.tsx
- Creates optimized production image
- Takes ~3-5 minutes

### Step 2b: Build Call Center Backend Image
```bash
cd /var/www/avatar

# Build the call center backend with new voice config
docker build \
  -f callCenter/Dockerfile \
  -t avatar-callcenter:voice-call \
  ./callCenter
```

**Expected output:**
```
Successfully tagged avatar-callcenter:voice-call
```

**What this does:**
- Installs Python dependencies
- Copies config.py with TTS settings
- Sets up supervisor for multi-process management
- Takes ~2-3 minutes

### Step 2c: Build Avatar Backend Image
```bash
cd /var/www/avatar

# Build the avatar backend (no changes, but needed for full stack)
docker build \
  -f avatary/Dockerfile \
  -t avatar-backend:latest \
  ./avatary
```

**Expected output:**
```
Successfully tagged avatar-backend:latest
```

### Step 2d: Verify Images Built Successfully
```bash
docker images | grep avatar

# Should show:
# avatar-frontend        voice-call
# avatar-callcenter      voice-call
# avatar-backend         latest
```

---

## Part 3: Create Docker Compose Override (Optional but Recommended)

Create a file for development override to mount code as volumes:

**File:** `/var/www/avatar/docker-compose.override.yml`
```yaml
version: '3.8'

services:
  frontend:
    image: avatar-frontend:voice-call
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules

  callcenter:
    image: avatar-callcenter:voice-call
    build: ./callCenter
    volumes:
      - ./callCenter:/app
      - /app/venv

  backend:
    image: avatar-backend:latest
    build: ./avatary
    volumes:
      - ./avatary:/app
      - /app/venv
```

This allows:
- Hot reloading during development
- Live code changes without rebuild
- Easier debugging

---

## Part 4: Start Services

### Step 4a: Prepare Environment
```bash
cd /var/www/avatar

# Use .env.docker for environment variables
cp .env.docker .env

# OR if you have a production .env, verify it has all variables:
# Make sure these are set:
# - LIVEKIT_URL
# - LIVEKIT_API_KEY
# - LIVEKIT_API_SECRET
# - OPENAI_API_KEY
```

### Step 4b: Start Docker Compose
```bash
cd /var/www/avatar

# Start all services
docker-compose up -d

# Expected output:
# Creating avatar-redis... done
# Creating avatar-backend... done
# Creating avatar-callcenter... done
# Creating avatar-frontend... done
```

### Step 4c: Check Service Status
```bash
docker-compose ps

# Expected output:
# NAME                  STATUS
# avatar-redis          Up X seconds (healthy)
# avatar-backend        Up X seconds (healthy)
# avatar-callcenter     Up X seconds (healthy)
# avatar-frontend       Up X seconds (healthy)
```

---

## Part 5: Test Services

### Step 5a: Check Frontend Health
```bash
curl -s http://localhost:3000/

# Expected: HTML content (home page)
```

Or open in browser: `http://localhost:3000`

### Step 5b: Check Call Center API Health
```bash
curl -s http://localhost:8000/health | jq .

# Expected:
# {"status": "ok"}
```

### Step 5c: Check Backend Logs
```bash
docker logs avatar-backend -f

# Look for:
# ✅ "Agent initialized"
# ✅ "Listening for incoming calls"
# ⚠️ Any connection errors?
```

### Step 5d: Check Call Center Logs
```bash
docker logs avatar-callcenter -f

# Look for:
# ✅ "Call Center Agent starting..."
# ✅ "Listening for incoming calls..."
# ✅ "TTS settings loaded"
```

### Step 5e: Check Redis Connection
```bash
docker logs avatar-redis

# Look for:
# ✅ "Ready to accept connections"
```

---

## Part 6: Test Voice Call Flow

### Step 6a: Access Frontend
```
Browser: http://localhost:3000/callcenter/call-with-audio?room=test-call-1&user=test-user
```

### Step 6b: Monitor Logs in Real-Time
Open 3 terminals:

**Terminal 1 - Frontend logs:**
```bash
docker logs -f avatar-frontend
```

**Terminal 2 - Call Center logs:**
```bash
docker logs -f avatar-callcenter
```

**Terminal 3 - Backend logs:**
```bash
docker logs -f avatar-backend
```

### Step 6c: Test Call Sequence

1. **Open the page**
   - Should see: "Initializing call..."
   - Check logs for: "🔌 Connecting to LiveKit..."

2. **Wait for connection**
   - Should see status change to "Connecting..."
   - Check logs for: "✅ Connected to LiveKit room"

3. **Agent dispatch**
   - Should see: "Waiting for agent..."
   - Check logs for: "🚀 Dispatching agent to room..."

4. **Agent joins**
   - Should see: "Agent Connected"
   - Listen for welcome message in Arabic/English
   - Check logs for: "✅ Audio attached and playing"

5. **Speak into microphone**
   - Microphone indicator should show audio levels
   - Check logs for: "User: [your speech]"

6. **Hear agent response**
   - Should hear voice response
   - Check logs for: "🤖 Agent: [response text]"

---

## Part 7: Troubleshooting

### Issue: Frontend container won't start

```bash
# Check logs
docker logs avatar-frontend

# Common issues:
# - Build args not passed correctly
# - Node version incompatible
# - Package installation failed

# Fix: Rebuild with verbose output
docker build \
  --build-arg NEXT_PUBLIC_LIVEKIT_URL="..." \
  -f frontend/Dockerfile \
  -t avatar-frontend:voice-call \
  --progress=plain \
  ./frontend
```

### Issue: Call Center container won't start

```bash
# Check logs
docker logs avatar-callcenter

# Common issues:
# - Python dependencies not installed
# - Supervisor config missing
# - Missing environment variables

# Fix: Check requirements.txt and supervisord.conf
ls -la /var/www/avatar/callCenter/requirements.txt
ls -la /var/www/avatar/callCenter/supervisord.conf
```

### Issue: No audio from agent

```bash
# Check Call Center logs for TTS errors
docker logs avatar-callcenter | grep -i "tts\|error"

# Check if OpenAI API key is set
docker exec avatar-callcenter env | grep OPENAI_API_KEY

# Check if LiveKit connection is working
docker logs avatar-callcenter | grep -i "livekit"
```

### Issue: Connection timeout

```bash
# Check if LiveKit URL is accessible
curl -v wss://tavus-agent-project-i82x78jc.livekit.cloud/health

# Check network connectivity
docker exec avatar-frontend curl -v http://localhost:8000/health
```

### Issue: "Cannot find module"

```bash
# If TypeScript errors in frontend build:
# This usually means missing dependencies

# Rebuild frontend from scratch
docker system prune -f
docker build \
  --build-arg NEXT_PUBLIC_LIVEKIT_URL="..." \
  --no-cache \
  -f frontend/Dockerfile \
  -t avatar-frontend:voice-call \
  ./frontend
```

---

## Part 8: Cleanup

### Stop All Services
```bash
docker-compose down

# With volume cleanup:
docker-compose down -v
```

### Remove Images
```bash
docker rmi avatar-frontend:voice-call
docker rmi avatar-callcenter:voice-call
docker rmi avatar-backend:latest
```

### Clean Docker System
```bash
# Remove unused images, containers, networks
docker system prune

# More aggressive cleanup
docker system prune -a
```

---

## Part 9: Performance Verification

### Check Container Resource Usage
```bash
docker stats

# Monitor CPU, memory, network I/O
# Press Ctrl+C to stop
```

### Expected Resource Usage:
- **Frontend:** ~150MB RAM
- **Call Center:** ~300MB RAM
- **Backend:** ~500MB RAM
- **Redis:** ~50MB RAM
- **Total:** ~1GB RAM

---

## Part 10: Production Deployment Checklist

- [ ] All images built successfully
- [ ] All services start without errors
- [ ] Health checks passing
- [ ] Frontend loads in browser
- [ ] API health endpoints responding
- [ ] Logs show no errors
- [ ] Voice call connects successfully
- [ ] Audio works end-to-end
- [ ] No resource leaks observed
- [ ] All environment variables configured

---

## Docker Build Commands Quick Reference

```bash
# Build all images
docker build -f frontend/Dockerfile -t avatar-frontend:voice-call ./frontend
docker build -f callCenter/Dockerfile -t avatar-callcenter:voice-call ./callCenter
docker build -f avatary/Dockerfile -t avatar-backend:latest ./avatary

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker system prune -a
```

---

## What Changed in This Implementation

**Frontend Image:**
- ✅ Includes new call-with-audio.tsx with WebRTC streaming
- ✅ LiveKit client library properly imported
- ✅ All dependencies installed
- ✅ Production build optimized

**Call Center Image:**
- ✅ Includes config.py with TTS settings
- ✅ Voice configuration loaded
- ✅ OpenAI TTS configured
- ✅ LiveKit agent properly configured

**Backend Image:**
- ✅ Unchanged (already correct pattern)
- ✅ Supports avatar video calls
- ✅ Ready to handle dispatched agents

---

## Next Steps After Docker Testing

1. ✅ **Docker Build:** Complete
2. ✅ **Docker Test:** Complete
3. ⏳ **Staging Deployment:** Test in staging environment
4. ⏳ **Integration Tests:** Run full test suite
5. ⏳ **Production Deployment:** Deploy to production
6. ⏳ **Monitoring:** Set up monitoring and alerts

---

## Support & Documentation

- **Code Review:** See `CODE_REVIEW.md`
- **Implementation Details:** See `VOICE_CALL_IMPLEMENTATION_STATUS.md`
- **Quick Reference:** See `QUICK_FIX_REFERENCE.md`

---

**Ready to Build?** Start with **Part 2: Build Images**

Good luck! 🚀
