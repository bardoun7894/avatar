# Avatar Backend (Avatary) Setup - Complete ✅

## Architecture Overview

Your application now uses the **Avatar Backend (avatary)** for LiveKit calls:

```
User Browser
    ↓
Frontend (Next.js) - Generates Token via /api/token
    ↓
LiveKit Cloud (wss://tavus-agent-project-i82x78jc.livekit.cloud)
    ↓
Avatar Backend (avatary) - LiveKit Agent Worker
```

---

## Components

### 1. **Frontend** (Next.js)
- **Location**: `/var/www/avatar/frontend`
- **Token Generation**: `/pages/api/token.ts`
- **Video Call Component**: `/components/VideoCallInterface.tsx`
- **URL**: https://pro.beldify.com

### 2. **Avatar Backend** (avatary)
- **Location**: `/var/www/avatar/avatary`
- **Main Agent**: `agent.py`
- **Type**: LiveKit Agent Worker (not HTTP API)
- **Function**: Handles AI conversations, voice, vision processing
- **Port**: 8080 (internal)

### 3. **LiveKit Cloud**
- **URL**: `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- **API Key**: `APIJL8zayDiwTwV`
- **Function**: Real-time audio/video infrastructure

---

## How It Works

### Step 1: User Starts Call
```typescript
// Frontend: User clicks "Start Call"
// Redirects to /call?room=ornina-123&user=Guest
```

### Step 2: Frontend Generates Token
```typescript
// Frontend calls its own API route
const response = await fetch('/api/token', {
  method: 'POST',
  body: JSON.stringify({
    roomName: 'ornina-123',
    identity: 'Guest'
  })
})
```

### Step 3: Next.js API Generates JWT
```typescript
// /pages/api/token.ts
import { AccessToken } from 'livekit-server-sdk'

const at = new AccessToken(
  process.env.LIVEKIT_API_KEY,
  process.env.LIVEKIT_API_SECRET,
  { identity: 'Guest', ttl: '1h' }
)

at.addGrant({
  room: 'ornina-123',
  roomJoin: true,
  canPublish: true,
  canSubscribe: true,
})

const token = await at.toJwt()
```

### Step 4: Frontend Connects to LiveKit
```typescript
const room = new Room()
await room.connect(
  'wss://tavus-agent-project-i82x78jc.livekit.cloud',
  token
)
```

### Step 5: Avatar Agent Joins
```python
# avatary/agent.py
# LiveKit Agent Worker automatically joins the room
# Handles conversation with AI, voice synthesis, etc.
```

---

## Key Differences from Call Center

| Feature | Avatar Backend (avatary) | Call Center |
|---------|-------------------------|-------------|
| **Type** | LiveKit Agent Worker | FastAPI HTTP API |
| **Token Generation** | Frontend API route | Backend endpoint |
| **Purpose** | AI conversations with video avatar | Audio-only call center |
| **Port** | 8080 (internal) | 8000 (HTTP API) |
| **Focus** | ✅ **Current Setup** | Alternative option |

---

## Environment Variables

### Frontend `.env` (Production)
```bash
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA

# Frontend uses these to generate tokens
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
```

### Avatar Backend `.env`
```bash
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA
OPENAI_API_KEY=sk-proj-...
TAVUS_API_KEY=997cdfe4f0b44ccaabb7c4e651bbb705
ELEVENLABS_API_KEY=sk_8486e31b70b9f98f998e38f6d55064a3f62242f948ef9967
```

---

## Current Status ✅

- ✅ Frontend deployed at https://pro.beldify.com
- ✅ Token generation working via `/api/token`
- ✅ Avatar Backend connected to LiveKit Cloud
- ✅ SSL/HTTPS enabled
- ✅ All services healthy

---

## Testing

### 1. Test Frontend
```bash
curl https://pro.beldify.com
```

### 2. Test Token Generation
Open browser console at https://pro.beldify.com/call?room=test&user=Guest

You should see:
```
🔑 Requesting token from /api/token...
📊 Token response status: 200
✅ Token received successfully
🔌 Connecting to LiveKit...
```

### 3. Check Avatar Backend Logs
```bash
ssh root@184.174.37.148 "docker logs -f avatar-backend"
```

Should show:
```
registered worker with LiveKit Cloud
```

---

## Troubleshooting

### Issue: "Failed to get token: 404"
**Solution**: Frontend now uses `/api/token` (Next.js API route), not Call Center

### Issue: "LiveKit server not found"
**Solution**: Check LIVEKIT_URL in environment variables

### Issue: "Agent not joining room"
**Solution**: Check avatar-backend container logs for errors

---

## Files Modified

1. `/frontend/components/VideoCallInterface.tsx` - Token request endpoint
2. `/frontend/pages/api/token.ts` - Token generation (already existed)
3. `/.env.production` - Environment variables

---

**Setup Complete!** Your Avatar application is now using the avatary backend for AI conversations with video avatars.
