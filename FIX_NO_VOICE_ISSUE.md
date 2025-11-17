# Fix: No Voice Issue

## Problem
Users can see the video avatar but there's no voice/audio. The agent worker is running but not joining rooms automatically.

## Root Cause
The LiveKit agent worker is registered and waiting, but it's not automatically joining rooms when users connect through the frontend. The agent's `entrypoint` function is never being called.

## Current Status
✅ Backend container running
✅ Agent worker registered with LiveKit  
✅ TTS configured (OpenAI "onyx" voice)
✅ Tavus credentials set
❌ Agent not joining rooms automatically
❌ No audio being produced

## Solutions

### Option 1: Configure Auto-Join Pattern (Recommended)

Update the agent to automatically join rooms based on a pattern:

```python
# In avatary/agent.py - at the bottom
if __name__ == "__main__":
    # Auto-join all rooms that start with "ornina-"
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Configure worker to auto-join rooms
            request_fnc=None,  # Join all rooms
            # Or specify a pattern:
            # room_name_pattern="ornina-*"
        )
    )
```

### Option 2: Manual Dispatch (Current Approach - Needs Fix)

The frontend calls `/api/dispatch-agent` which tries to dispatch the agent, but this is timing out. We need to:

1. **Fix the dispatch method** - Use LiveKit's Agent Dispatch API properly
2. **Or use LiveKit Jobs API** to explicitly dispatch the agent

```typescript
// In frontend/pages/api/dispatch-agent.ts
// Instead of updateRoomMetadata, use proper agent dispatch:

import { AgentDispatch } from 'livekit-server-sdk'

const dispatch = new AgentDispatch(httpUrl, apiKey, apiSecret)
await dispatch.createDispatch({
  room: roomName,
  agent_name: 'ornina-avatar-agent'
})
```

### Option 3: Use LiveKit Cloud Dashboard

1. Go to LiveKit Cloud Dashboard
2. Navigate to "Agents" section
3. Configure auto-dispatch rules for your agent
4. Set pattern: `ornina-*` to auto-join all ornina rooms

---

## Quick Test

### 1. Check Agent Status
```bash
docker logs avatar-backend --tail 100 | grep -E "(registered worker|NEW CONNECTION)"
```

You should see:
- ✅ `"registered worker"` - Agent connected to LiveKit
- ❌ No "NEW CONNECTION" - Agent not joining rooms

### 2. Test Manual Connection

Create a room and manually trigger agent:

```bash
# Connect to frontend
curl http://localhost:3000

# Watch backend logs in real-time
docker logs -f avatar-backend
```

If you see "NEW CONNECTION!" when connecting, the agent is working.

---

## Temporary Fix (Test Voice Immediately)

To test if voice works at all, you can force the agent to join ANY room:

```python
# In avatary/agent.py, modify the WorkerOptions:

if __name__ == "__main__":
    import sys
    
    # Add debugging
    print("🚀 Starting agent worker...")
    print(f"LiveKit URL: {os.environ.get('LIVEKIT_URL')}")
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Accept all room join requests
            request_fnc=lambda ctx: True  # Join ANY room
        )
    )
```

Rebuild and restart:
```bash
cd /var/www/avatar
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

---

## Verification Steps

### 1. Agent Joins Room
```bash
# Watch logs
docker logs -f avatar-backend

# Connect from frontend
# You should see:
# "NEW CONNECTION!"
# "Avatar Mode: TAVUS"
# "Voice: OpenAI Onyx"
```

### 2. Audio is Produced
Check browser console for:
```
🎥 Track subscribed: audio from tavus-avatar-agent
✅ Remote audio attached and playing
```

### 3. Test with Simple Room

Use LiveKit's test page:
```
https://meet.livekit.io/custom?url=wss://tavus-agent-project-i82x78jc.livekit.cloud&token=YOUR_TOKEN
```

If agent joins and speaks there, the issue is in your frontend.
If agent doesn't join, the issue is in agent configuration.

---

## Long-Term Solution

### Update Agent Configuration

```python
# avatary/agent.py

# Add request handler to accept all Ornina rooms
def should_join_room(ctx: agents.JobRequest) -> bool:
    """Decide if agent should join this room"""
    room_name = ctx.room.name
    
    # Join all ornina rooms
    if room_name.startswith("ornina-"):
        print(f"✅ Accepting room: {room_name}")
        return True
    
    # Join test rooms
    if room_name.startswith("test-"):
        print(f"✅ Accepting test room: {room_name}")
        return True
    
    print(f"❌ Rejecting room: {room_name}")
    return False

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            request_fnc=should_join_room  # Use custom handler
        )
    )
```

---

## Debug Checklist

- [ ] Agent worker registered with LiveKit
- [ ] Environment variables set (LIVEKIT_URL, API_KEY, API_SECRET)
- [ ] Tavus credentials configured
- [ ] OpenAI TTS configured
- [ ] Agent entrypoint being called (check for "NEW CONNECTION" in logs)
- [ ] Agent session created successfully
- [ ] Audio tracks being published by agent
- [ ] Frontend receiving and playing audio tracks

---

## Common Issues

### Issue: "registered worker" but no "NEW CONNECTION"
**Cause:** Agent not configured to auto-join rooms  
**Fix:** Add `request_fnc` or configure auto-dispatch in LiveKit Cloud

### Issue: "NEW CONNECTION" but no audio in browser
**Cause:** Frontend not subscribing to audio tracks  
**Fix:** Check VideoCallInterface.tsx audio track subscription code

### Issue: Agent joins but crashes immediately
**Cause:** Missing dependencies or configuration error  
**Fix:** Check full agent logs for Python exceptions

---

## Next Steps

1. **Immediate:** Add `request_fnc=lambda ctx: True` to test if agent works at all
2. **Short-term:** Implement proper room pattern matching
3. **Long-term:** Configure LiveKit Cloud auto-dispatch rules

---

**Status:** Diagnosis complete, awaiting fix implementation  
**Priority:** HIGH - No voice = Core feature broken  
**ETA:** 5-10 minutes to implement and test fix

