# LiveKit "Failed to fetch" - Quick Fix Guide

## The Issue
When starting an avatar video call, you see: **"Failed to connect to LiveKit: Failed to fetch"**

---

## Quick Diagnosis

### Step 1: Run the Diagnostic
```bash
/var/www/avatar/scripts/diagnose-livekit.sh
```

**If all checks pass (✅):** The issue is likely on your **browser/network side**. Skip to "Browser-Side Fixes".

**If any check fails (✗):** Follow the specific fix below.

---

## Step 2: Browser-Side Fixes

### 2A: Check Browser Console
1. Open the avatar video call page
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Try to start the video call
5. Look for error messages with 🔌 or ❌

### 2B: Common Browser Issues

| What You See | Fix |
|---|---|
| Network error/timeout | Check internet connection |
| 401 Unauthorized | Wait 5 minutes and retry (token might be expired) |
| CORS error | This is normal, should still work |
| WebSocket closed | Refresh page and try again |

### 2C: Clear Cache & Retry
1. **Chrome/Edge:** Ctrl+Shift+Delete (or Cmd+Shift+Delete)
2. Select "All time"
3. Check "Cookies and other site data"
4. Click "Clear data"
5. Refresh the page and try again

---

## Step 3: Server-Side Fixes

### 3A: Check Environment Variables
```bash
# Verify .env exists
ls /var/www/avatar/.env

# Check LiveKit URL is set correctly
grep "NEXT_PUBLIC_LIVEKIT_URL" /var/www/avatar/.env
```

Should show something like: `NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud`

### 3B: Rebuild Frontend (if env changed)
```bash
cd /var/www/avatar
docker-compose build frontend
docker-compose up -d frontend
```

Wait 30-60 seconds for frontend to be ready.

### 3C: Verify Container is Running
```bash
docker-compose ps

# Should show avatar-frontend as "healthy"
```

---

## Step 4: Advanced Troubleshooting

### Check Full Logs
```bash
# See detailed error messages
docker-compose logs frontend -f --tail 100

# In browser console, look for these patterns:
# - "🔌 Connecting to LiveKit..."
# - "🔑 Connecting with token..."
# - "❌ LiveKit connection error:"
```

### Test Token Generation Directly
```bash
curl -X POST http://localhost:3000/api/token \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test","identity":"user1"}'

# Should return a token (long JWT string)
```

If this fails, the frontend API is broken.

### Check Network in Browser
1. Open DevTools (F12)
2. Go to **Network** tab
3. Try to make a video call
4. Look for failed requests
5. Click on failed request to see response

---

## Most Common Fix (90% of cases)

The issue is usually a **temporary network glitch** or **expired session**:

```bash
# 1. Refresh the page (Ctrl+F5 or Cmd+Shift+R for hard refresh)
# 2. Wait 10 seconds for frontend to be ready
# 3. Try again
```

If that doesn't work:

```bash
# 2. Restart the frontend container
docker-compose down frontend
docker-compose up -d frontend

# Wait 30 seconds, then try again
```

---

## If You Still Can't Connect

1. **Check internet connection** - Can you access other websites?
2. **Check firewall** - Does it block port 443 (WebSocket)?
3. **Verify credentials** - Are the LiveKit API keys still valid?
4. **Check browser console** - What's the exact error message?
5. **Read full guide** - See `LIVEKIT_TROUBLESHOOTING.md` for detailed help

---

## Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Connection times out | Network unreachable | Check internet, firewall |
| 401 error | Invalid token | Refresh page, rebuild frontend |
| Page won't load | Frontend crashed | `docker-compose restart frontend` |
| Token endpoint fails | Backend misconfigured | Check `.env` file |
| "Failed to fetch" | Network issue | Hard refresh (Ctrl+F5), restart container |

---

## Recovery Checklist

```bash
# Step 1: Hard refresh browser (Ctrl+F5)
# Step 2: Run diagnostic
/var/www/avatar/scripts/diagnose-livekit.sh

# Step 3: If diagnostic shows errors, fix .env
nano /var/www/avatar/.env

# Step 4: Rebuild if changed
docker-compose build frontend && docker-compose up -d frontend

# Step 5: Check logs
docker-compose logs frontend --tail 50

# Step 6: Try again
# - Open browser console (F12)
# - Go to video call page
# - Look for 🔌 or ❌ messages with detailed error
```

---

## For Support

**When reporting issues, provide:**
1. Browser type and version (e.g., Chrome 130.0)
2. Exact error message from console
3. Output of: `/var/www/avatar/scripts/diagnose-livekit.sh`
4. Recent logs: `docker-compose logs frontend --tail 100`

This info helps identify the issue quickly.

---

**Last Updated:** November 11, 2025
**System Version:** Avatar v2.0
