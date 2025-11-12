# LiveKit Connection Issue - Fixed ✅

## Problem
Frontend was showing: **"Failed to connect to LiveKit: LiveKit server not found"**

## Root Cause
The `NEXT_PUBLIC_API_URL` environment variable was pointing to:
```
https://184.174.37.148:8000
```

This caused issues because:
1. Port 8000 is not directly exposed with HTTPS
2. The frontend needs to use the Nginx reverse proxy
3. Direct IP:port access bypasses SSL/TLS security

## Solution
Changed the API URL to use the domain with Nginx proxy:
```bash
# Before (❌ Wrong)
NEXT_PUBLIC_API_URL=https://184.174.37.148:8000

# After (✅ Correct)
NEXT_PUBLIC_API_URL=https://pro.beldify.com/api
```

## What Was Fixed
1. **Updated `.env.production`** with correct API URL
2. **Rebuilt frontend container** with new environment variables
3. **Redeployed frontend** with updated configuration

## Nginx Proxy Configuration
The Nginx reverse proxy now properly routes:
- `https://pro.beldify.com/` → Frontend (port 3001)
- `https://pro.beldify.com/api/` → Call Center API (port 8000)
- `https://pro.beldify.com/ws` → WebSocket for LiveKit
- `https://pro.beldify.com/health` → Health check endpoint

## Verification
All services are now working correctly:

```bash
# Test HTTPS site
curl https://pro.beldify.com

# Test API health
curl https://pro.beldify.com/health
# Response: {"status":"healthy","active_calls":0,...}

# Check LiveKit connection
docker logs avatar-backend | grep LiveKit
# Shows: registered worker with LiveKit Cloud
```

## Current Status ✅
- ✅ Frontend: https://pro.beldify.com (working)
- ✅ API: https://pro.beldify.com/api/ (working)
- ✅ LiveKit: Connected to Cloud (wss://tavus-agent-project-i82x78jc.livekit.cloud)
- ✅ SSL/TLS: Valid certificate from Let's Encrypt
- ✅ All containers: Healthy

## Architecture
```
Internet
    ↓
Nginx (443) - SSL/TLS Termination
    ↓
    ├─→ Frontend (3001) - Next.js
    ├─→ API (8000) - FastAPI Call Center
    ├─→ Backend (8080) - Avatar Agent
    └─→ Redis (6379) - Cache
         ↓
    LiveKit Cloud (wss://)
```

## Files Modified
1. `/var/www/avatar/.env.production` - Updated NEXT_PUBLIC_API_URL
2. Frontend container rebuilt with new environment

## Commands Used
```bash
# Update environment
./update-production-env.sh

# Rebuild frontend
docker-compose build --no-cache frontend

# Restart frontend
docker stop avatar-frontend
docker run -d --name avatar-frontend-new \
  --network avatar_avatar-network \
  -p 3001:3000 \
  --env-file /tmp/avatar-deploy/.env \
  ornina-avatar-frontend:latest
```

## Prevention
To avoid this issue in the future:
1. Always use domain names (not IP:port) in production
2. Route all traffic through Nginx reverse proxy
3. Use environment-specific .env files
4. Test API connectivity after deployment

## Next Steps
1. ✅ Test the application at https://pro.beldify.com
2. ✅ Verify LiveKit calls are working
3. ✅ Monitor logs for any errors
4. ✅ Setup monitoring alerts

---

**Issue Resolved**: Wed Nov 12, 2025 03:09 CET
**Fixed By**: Automated deployment script with corrected environment variables
