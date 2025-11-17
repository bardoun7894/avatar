# LiveKit Connection Issues - Troubleshooting Guide

**Created**: November 12, 2025  
**Purpose**: Complete guide to diagnose and fix LiveKit connection problems

---

## 🚨 Common LiveKit Issues We've Encountered

### Issue 1: Agent Not Joining Room
**Symptoms**:
- User connects successfully
- Token generation works (200 OK)
- Agent dispatch request sent
- Agent never joins the room
- Connection disconnects after timeout

### Issue 2: Tavus API Authentication Error (401)
**Symptoms**:
```
APIStatusError: Server returned an error (status_code=401)
body={"message":"Invalid access token"}
```

### Issue 3: Missing Python Import (NameError)
**Symptoms**:
```
NameError: name 'datetime' is not defined
```

### Issue 4: Frontend Token Generation 404
**Symptoms**:
```
Failed to load resource: the server responded with a status of 404 ()
GET /api/token 404
```

---

## 📋 Complete Diagnostic Checklist

### Step 1: Check Container Status

```bash
# SSH to production server
ssh root@184.174.37.148

# Check all containers are running
docker ps | grep avatar

# Expected output:
# avatar-frontend  - Running on port 3001
# avatar-backend   - Running on port 8080
# avatar-callcenter - Running on port 8000
# avatar-redis     - Running on port 6379
```

**If containers are not running**:
```bash
cd /tmp/avatar-deploy
docker-compose up -d
```

---

### Step 2: Check Avatar Backend Logs

```bash
# View recent logs
docker logs --tail 100 avatar-backend

# Look for these SUCCESS indicators:
✅ "registered worker" - Agent connected to LiveKit Cloud
✅ "Face recognition available" - Vision system ready
✅ "process initialized" - Worker processes started

# Look for these ERROR indicators:
❌ "failed to call tavus api" - Tavus API key invalid
❌ "NameError" - Missing Python import
❌ "401" or "403" - Authentication error
❌ "Connection refused" - Network issue
```

---

### Step 3: Verify Environment Variables

```bash
# Check Tavus API key in container
docker exec avatar-backend env | grep TAVUS_API_KEY

# Check LiveKit credentials
docker exec avatar-backend env | grep LIVEKIT

# Expected values:
TAVUS_API_KEY=1683bc5e621a49a287c3c558909e7f4b
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA
```

**If values are wrong**:
```bash
# Update .env.production locally
nano /var/www/avatar/.env.production

# Upload to server
scp .env.production root@184.174.37.148:/tmp/avatar-deploy/avatary/.env

# Restart backend
docker stop avatar-backend && docker rm avatar-backend
docker run -d --name avatar-backend \
  --network avatar_avatar-network \
  -p 8080:8080 \
  --env-file /tmp/avatar-deploy/avatary/.env \
  ornina-avatar-backend:latest
```

---

### Step 4: Test Token Generation

```bash
# Test token API endpoint
curl -X POST https://pro.beldify.com/api/token \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test-room","identity":"test-user"}'

# Expected response:
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "livekit_url": "wss://tavus-agent-project-i82x78jc.livekit.cloud"
}

# If 404 error:
# - Check Nginx routing
# - Verify frontend container is running
# - Check /api/token route exists in frontend
```

---

### Step 5: Check Nginx Configuration

```bash
# View Nginx config
cat /etc/nginx/sites-available/avatar

# Verify these routes exist:
location ~ ^/api/(token|dispatch-agent) {
    proxy_pass http://localhost:3001;  # Frontend Next.js API
}

location /api/ {
    proxy_pass http://localhost:8000/;  # Call Center API
}

# Test Nginx config
nginx -t

# Reload if needed
systemctl reload nginx
```

---

## 🔧 Solution Procedures

### Solution 1: Fix Tavus API Key Error

**Problem**: `401 Invalid access token` from Tavus API

**Steps**:

1. **Get new API key** from Tavus dashboard

2. **Update .env.production**:
```bash
# Edit locally
nano /var/www/avatar/.env.production

# Change line 38:
TAVUS_API_KEY=YOUR_NEW_API_KEY_HERE
```

3. **Deploy to production**:
```bash
# Upload
scp .env.production root@184.174.37.148:/tmp/avatar-deploy/avatary/.env

# Rebuild backend
ssh root@184.174.37.148 "cd /tmp/avatar-deploy && docker-compose build backend"

# Restart
ssh root@184.174.37.148 "docker stop avatar-backend && docker rm avatar-backend"
ssh root@184.174.37.148 "docker run -d --name avatar-backend \
  --network avatar_avatar-network -p 8080:8080 \
  --env-file /tmp/avatar-deploy/avatary/.env \
  ornina-avatar-backend:latest"
```

4. **Verify**:
```bash
docker logs --tail 30 avatar-backend | grep -i tavus
# Should NOT see "401" or "Invalid access token"
```

---

### Solution 2: Fix Missing Python Import

**Problem**: `NameError: name 'datetime' is not defined`

**Steps**:

1. **Add import to agent.py**:
```python
# File: /var/www/avatar/avatary/agent.py
# Add this line around line 23:

from datetime import datetime
```

2. **Deploy**:
```bash
scp avatary/agent.py root@184.174.37.148:/tmp/avatar-deploy/avatary/
ssh root@184.174.37.148 "cd /tmp/avatar-deploy && docker-compose build backend"
ssh root@184.174.37.148 "docker stop avatar-backend && docker rm avatar-backend"
ssh root@184.174.37.148 "docker run -d --name avatar-backend \
  --network avatar_avatar-network -p 8080:8080 \
  --env-file /tmp/avatar-deploy/avatary/.env \
  ornina-avatar-backend:latest"
```

3. **Verify**:
```bash
docker logs --tail 30 avatar-backend | grep -i error
# Should NOT see "NameError"
```

---

### Solution 3: Fix Token API 404 Error

**Problem**: `/api/token` returns 404

**Root Cause**: Nginx routing or frontend not running

**Steps**:

1. **Check frontend is running**:
```bash
docker ps | grep avatar-frontend
curl http://localhost:3001/api/token -X POST \
  -d '{"roomName":"test","identity":"user"}'
```

2. **Verify Nginx routing**:
```bash
# Check Nginx config
cat /etc/nginx/sites-available/avatar | grep -A 5 "location.*token"

# Should route to frontend (port 3001), NOT callcenter (port 8000)
```

3. **Fix Nginx if needed**:
```bash
# Edit config
nano /etc/nginx/sites-available/avatar

# Ensure this block comes BEFORE /api/ block:
location ~ ^/api/(token|dispatch-agent) {
    proxy_pass http://localhost:3001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Test and reload
nginx -t
systemctl reload nginx
```

---

### Solution 4: Agent Not Joining Room

**Problem**: User connects but agent doesn't join

**Diagnostic Steps**:

1. **Check agent dispatch**:
```bash
# Watch backend logs in real-time
docker logs -f avatar-backend

# In another terminal, make a test call
# Look for:
✅ "Conversation started: [room-name]"
✅ "Connecting to room..."
✅ "Starting Tavus video avatar..."
```

2. **Common causes**:
   - Tavus API error (see Solution 1)
   - Python import error (see Solution 2)
   - Agent not registered with LiveKit Cloud
   - Network connectivity issue

3. **Verify agent registration**:
```bash
docker logs avatar-backend | grep "registered worker"

# Should see:
{"message": "registered worker", "url": "wss://tavus-agent-project-i82x78jc.livekit.cloud"}
```

4. **If not registered**:
```bash
# Check LiveKit credentials
docker exec avatar-backend env | grep LIVEKIT

# Restart backend
docker restart avatar-backend

# Wait 10 seconds and check again
sleep 10
docker logs avatar-backend | grep "registered worker"
```

---

## 🧪 Complete Test Procedure

After fixing any issue, run this complete test:

### 1. Backend Health Check
```bash
# All should return success
docker ps | grep avatar-backend
docker logs --tail 20 avatar-backend | grep "registered worker"
docker exec avatar-backend env | grep TAVUS_API_KEY
```

### 2. Frontend Health Check
```bash
curl -I https://pro.beldify.com
# Should return: HTTP/2 200
```

### 3. Token API Test
```bash
curl -X POST https://pro.beldify.com/api/token \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test","identity":"user"}' | jq
# Should return valid token and livekit_url
```

### 4. Live Call Test
1. Open: https://pro.beldify.com
2. Click: "ابدأ المحادثة / Start Call"
3. Allow camera/microphone
4. **Expected**:
   - ✅ User video appears
   - ✅ "Connecting to AI Avatar..." message
   - ✅ Agent joins within 5-10 seconds
   - ✅ Tavus video avatar appears
   - ✅ Agent greets user

---

## 📊 Quick Reference: Error Messages

| Error Message | Location | Solution |
|--------------|----------|----------|
| `Invalid access token` | Backend logs | Update Tavus API key (Solution 1) |
| `NameError: name 'datetime'` | Backend logs | Add datetime import (Solution 2) |
| `404 /api/token` | Browser console | Fix Nginx routing (Solution 3) |
| `Failed to connect to LiveKit` | Browser console | Check LiveKit credentials |
| `Agent dispatch request sent` but no join | Backend logs | Check Tavus API + registration |
| `Connection refused` | Backend logs | Check network/firewall |
| `Container not running` | Docker ps | Restart containers |

---

## 🔑 Critical Files & Locations

### Local Development
```
/var/www/avatar/.env.production          # Environment variables
/var/www/avatar/avatary/agent.py         # Agent code
/var/www/avatar/frontend/pages/api/token.ts  # Token generation
```

### Production Server
```
/tmp/avatar-deploy/.env                  # Frontend env
/tmp/avatar-deploy/avatary/.env          # Backend env
/etc/nginx/sites-available/avatar        # Nginx config
```

### Docker Containers
```
avatar-backend    - Port 8080 - LiveKit Agent
avatar-frontend   - Port 3001 - Next.js
avatar-callcenter - Port 8000 - FastAPI
avatar-redis      - Port 6379 - Redis
```

---

## 🚀 Emergency Quick Fix

If everything is broken and you need to get it working FAST:

```bash
# 1. SSH to server
ssh root@184.174.37.148

# 2. Stop all containers
docker stop avatar-backend avatar-frontend avatar-callcenter avatar-redis

# 3. Remove all containers
docker rm avatar-backend avatar-frontend avatar-callcenter avatar-redis

# 4. Restart everything
cd /tmp/avatar-deploy
docker-compose up -d

# 5. Wait 30 seconds
sleep 30

# 6. Check status
docker ps | grep avatar

# 7. Test
curl https://pro.beldify.com
```

---

## 📞 Support Checklist

When asking for help, provide:

1. **Error message** from browser console
2. **Backend logs**: `docker logs --tail 100 avatar-backend`
3. **Container status**: `docker ps | grep avatar`
4. **Environment check**: `docker exec avatar-backend env | grep TAVUS`
5. **What you tried**: List of solutions attempted

---

## 🎯 Prevention Tips

1. **Always test locally first** before deploying to production
2. **Check logs immediately** after deployment
3. **Verify environment variables** are loaded correctly
4. **Keep API keys updated** and secure
5. **Monitor Tavus API quota** and limits
6. **Use version control** for all configuration changes

---

## 📚 Related Documentation

- `TAVUS_API_FIX.md` - Tavus API key update guide
- `PRODUCTION_DEPLOYMENT_SUMMARY.md` - Latest deployment details
- `LIVEKIT_TOKEN_EXPLANATION.md` - How token generation works
- `DEPLOYMENT_COMPLETE.md` - Full deployment architecture

---

**Last Updated**: November 12, 2025  
**Tested On**: Production server 184.174.37.148  
**Status**: All issues documented and resolved ✅
