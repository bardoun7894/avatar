# LiveKit Connection Troubleshooting Guide

## Problem: "Failed to connect to LiveKit: Failed to fetch"

This error occurs when the browser cannot establish a WebSocket connection to the LiveKit server. Here's how to diagnose and fix the issue.

---

## Common Causes & Solutions

### 1. **Missing or Incorrect Environment Variables**

**Symptom:** Error occurs immediately when trying to connect

**Check:**
```bash
# Verify .env file exists in project root
ls -la /var/www/avatar/.env

# Check if NEXT_PUBLIC_LIVEKIT_URL is set
grep "NEXT_PUBLIC_LIVEKIT_URL" /var/www/avatar/.env
```

**Expected output:**
```
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
```

**Fix:**
- If file is missing, copy from `.env.example`:
  ```bash
  cp /var/www/avatar/.env.example /var/www/avatar/.env
  ```
- Update with your actual LiveKit credentials
- Rebuild the frontend:
  ```bash
  docker-compose build frontend
  docker-compose up -d frontend
  ```

---

### 2. **Network Connectivity Issues**

**Symptom:** Connection fails with "Failed to fetch" or timeout

**Diagnose:**
```bash
# Test DNS resolution
docker exec avatar-frontend nslookup tavus-agent-project-i82x78jc.livekit.cloud

# Expected output: IP addresses (161.115.161.153, 161.115.161.158)
```

**Fix:**
- Check internet connection on the host machine
- Verify firewall isn't blocking WebSocket connections (port 443)
- If behind a proxy, configure proxy settings in the Next.js app

---

### 3. **API Credentials Invalid or Expired**

**Symptom:** Token generation fails, 401 Unauthorized errors

**Check the credentials:**
```bash
# Test LiveKit API endpoint
curl -X GET "https://tavus-agent-project-i82x78jc.livekit.cloud/api/rooms" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

**Fix:**
- Verify `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` in `.env`
- Check if credentials have expired (contact LiveKit support)
- Regenerate credentials in LiveKit dashboard if needed
- Update `.env` file with new credentials
- Rebuild containers

---

### 4. **Browser Console Errors**

**Check the browser console for detailed errors:**

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for messages starting with "❌" or "🔌"

**Common error patterns:**

| Error | Cause | Fix |
|-------|-------|-----|
| `Failed to fetch` | Network/CORS issue | Check internet, firewall, proxy |
| `401 Unauthorized` | Invalid token/credentials | Verify API keys in `.env` |
| `404 Not Found` | Wrong LiveKit URL | Check `NEXT_PUBLIC_LIVEKIT_URL` |
| `WebSocket: connection failed` | Network connectivity | Check firewall, port 443 |
| `Invalid authorization header` | Token format issue | Check token generation in `/api/token` |

---

### 5. **CORS/WebSocket Issues**

**Symptom:** Browser blocks connection due to CORS

**Fix:**
- Ensure `NEXT_PUBLIC_LIVEKIT_URL` uses `wss://` (WebSocket Secure)
- Check that the LiveKit server allows connections from your domain
- If using custom domain, configure CORS in LiveKit settings

---

## Debugging Steps

### Step 1: Check Frontend Environment
```bash
docker exec avatar-frontend env | grep LIVEKIT

# Should output:
# NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
# LIVEKIT_API_KEY=APIJL8zayDiwTwV
# LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA
```

### Step 2: Test Token Generation
```bash
curl -X POST http://localhost:3000/api/token \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test","identity":"user1"}'

# Should return a JWT token
```

### Step 3: Check Browser Logs
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try to start a video call
4. Look for detailed error messages with 🔌 or ❌ prefix

### Step 4: Check Frontend Container Logs
```bash
docker-compose logs frontend -f --tail 50

# Look for errors related to token generation or connection attempts
```

---

## Current Configuration (as of Nov 11, 2025)

**LiveKit Server:**
- URL: `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- Type: Cloud-hosted (Tavus)
- Status: Verified reachable

**Frontend Setup:**
- Location: `/var/www/avatar/frontend`
- Container: `avatar-frontend` (port 3000)
- Built with: Next.js + React
- Token endpoint: `/api/token`

---

## Advanced Troubleshooting

### Increase Logging Level
Edit the frontend component and change logging level:
```typescript
// In VideoCallInterface.tsx
console.log = console.warn = console.info = console.debug = (msg) => console.log('[DEBUG]', msg)
```

### Test WebSocket Directly
```bash
# Install websocat if not present
apt-get install -y websocat

# Test WebSocket connection
websocat wss://tavus-agent-project-i82x78jc.livekit.cloud
```

### Check Container Health
```bash
docker-compose ps

# All containers should show "healthy" status
# If frontend shows "starting", wait for it to be ready
```

---

## Recent Changes (Nov 11, 2025)

Enhanced error logging has been added to both:
- `/var/www/avatar/frontend/components/VideoCallInterface.tsx`
- `/var/www/avatar/frontend/apps/avatar/components/VideoCallInterface.tsx`

**Improvements:**
- ✅ Detailed error messages in console
- ✅ Error type and stack trace logging
- ✅ Better error categorization (network, auth, WebSocket)
- ✅ Improved token generation logging

**To see new logging:**
1. Rebuild frontend: `docker-compose build frontend`
2. Restart frontend: `docker-compose up -d frontend`
3. Open browser DevTools (F12)
4. Console tab will show detailed logs with emoji prefixes

---

## Quick Fix Checklist

- [ ] `.env` file exists at `/var/www/avatar/.env`
- [ ] `NEXT_PUBLIC_LIVEKIT_URL` is set and uses `wss://`
- [ ] `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are valid
- [ ] Frontend container is running: `docker-compose ps`
- [ ] Token endpoint works: `curl http://localhost:3000/api/token`
- [ ] Browser can reach LiveKit server (check DevTools Network tab)
- [ ] No firewall blocking port 443 (WebSocket)
- [ ] Browser console shows detailed error messages

---

## Getting Help

If you still can't connect:
1. Check browser console for exact error (F12 → Console)
2. Run the debugging steps above
3. Check frontend container logs: `docker-compose logs frontend`
4. Verify LiveKit credentials are active and not expired
5. Contact LiveKit support if server is unreachable

For more info: [LiveKit Documentation](https://docs.livekit.io/)
