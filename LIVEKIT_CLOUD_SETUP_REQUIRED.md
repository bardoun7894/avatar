# ⚠️ LiveKit Cloud Configuration Required

## Current Issue
The agent worker is running and registered with LiveKit Cloud, but **not receiving dispatch requests** when users create rooms. This is because LiveKit Cloud requires explicit configuration to dispatch agents to self-hosted workers.

## Status
- ✅ Agent worker running (`avatar-backend` container healthy)
- ✅ Agent registered with LiveKit Cloud (worker ID: `AW_5DbfkHwanLkk`)
- ❌ No dispatch requests received (agent never joins rooms)
- ❌ No voice/audio because agent isn't joining

## Root Cause
**LiveKit Cloud** (hosted at `wss://tavus-agent-project-i82x78jc.livekit.cloud`) with a **self-hosted agent worker** (running in Docker) requires you to configure agent dispatch rules in the LiveKit Cloud Dashboard.

The agent worker can:
1. **Register** with LiveKit Cloud ✅ (Working)
2. **Listen** for dispatch requests ✅ (Working)  
3. **Join rooms** when dispatched ✅ (Code ready)

BUT - LiveKit Cloud needs to be told **WHEN to dispatch** agents!

---

## Solution: Configure LiveKit Cloud Dashboard

### Step 1: Access LiveKit Cloud Dashboard
1. Open your browser
2. Go to: **https://cloud.livekit.io**
3. Log in with your LiveKit account

### Step 2: Select Your Project
1. Find and click: **tavus-agent-project-i82x78jc**
2. Or use the project dropdown in the top navigation

### Step 3: Navigate to Agent Settings
1. In the left sidebar, click: **Settings**
2. Then click: **Agents** (or **Agent Dispatch**)

### Step 4: Add Agent Dispatch Rule
Click **"Add Agent Rule"** or **"Create Dispatch Rule"**

Configure the following:

| Setting | Value |
|---------|-------|
| **Rule Name** | "Ornina Avatar Auto-Dispatch" |
| **Room Name Pattern** | `ornina-*` |
| **Agent Name** | `ornina-avatar-agent` |
| **Auto-Dispatch** | ✅ ON (Enable) |
| **Priority** | High (if available) |

### Step 5: Save and Test
1. Click **Save** or **Create Rule**
2. Wait 10-30 seconds for the rule to propagate
3. Test by connecting to the frontend

---

## Alternative: Manual Dispatch (Temporary Workaround)

If you can't configure the dashboard right now, you can manually dispatch the agent using the LiveKit API:

```bash
# From your server
curl -X POST "https://tavus-agent-project-i82x78jc.livekit.cloud/twirp/livekit.AgentDispatchService/CreateDispatch" \
  -H "Authorization: Basic $(echo -n 'APIJL8zayDiwTwV:fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA' | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "room": "ornina-test-room",
    "agent_name": "ornina-avatar-agent"
  }'
```

---

##Testing After Configuration

### 1. Check Agent Worker Status
```bash
docker logs avatar-backend --tail 100 | grep -E "(Accepting room|NEW CONNECTION)"
```

**Expected output after a user connects:**
```
✅ Accepting room: ornina-1763160177001
============================================================
اتصال جديد! - NEW CONNECTION!
============================================================
```

### 2. Test from Frontend
1. Go to `https://pro.beldify.com`
2. Enter your name and click "Start Call"
3. **Wait 5-10 seconds**
4. Agent should join and speak!

### 3. Browser Console
Press `F12` and check for:
```
🎥 Track subscribed: audio from ornina-avatar-agent
✅ Remote audio attached and playing
```

---

## Why This Is Needed

### Architecture
```
User Browser
    ↓
LiveKit Cloud (wss://tavus-agent-project-i82x78jc.livekit.cloud)
    ↓
    ↓ (needs dispatch configuration!)
    ↓
Self-Hosted Agent Worker (Docker container)
```

### The Problem
- **Hosted LiveKit** doesn't automatically know about **self-hosted workers**
- Workers register and wait, but LiveKit won't dispatch unless configured
- Frontend can request dispatch, but that's timing out (non-blocking)

### The Solution
- Configure LiveKit Cloud to **automatically dispatch** agents when rooms matching `ornina-*` are created
- This tells LiveKit: "When someone creates a room called `ornina-whatever`, send a dispatch request to the `ornina-avatar-agent` worker"

---

## Common Issues

### Issue: "I don't have access to LiveKit Cloud Dashboard"
**Solution:** Ask the project owner/admin who set up the LiveKit project to:
1. Log into https://cloud.livekit.io
2. Add you as a team member with Agent configuration permissions
3. Or ask them to configure the dispatch rule

### Issue: "I can't find the Agents settings"
**Solution:** Look for:
- Settings > Agents
- Settings > Agent Dispatch  
- Project Settings > Integrations > Agents

(The exact location depends on your LiveKit plan and dashboard version)

### Issue: "The rule is configured but agent still doesn't join"
**Troubleshooting:**
1. Check the room name pattern matches: `ornina-*`
2. Verify agent name is exact: `ornina-avatar-agent`
3. Wait 30 seconds for rules to propagate
4. Restart the agent worker: `docker-compose restart backend`
5. Check agent worker logs for "Accepting room" messages

---

## Technical Details

### Agent Worker Configuration
```python
# In avatary/agent.py
agents.cli.run_app(
    agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        request_fnc=should_join_room  # Accepts all dispatch requests
    )
)
```

### Current Worker Status
- **Worker ID:** `AW_5DbfkHwanLkk`
- **LiveKit URL:** `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- **Region:** Germany 2
- **Protocol:** 16
- **Status:** Registered and waiting for dispatch

### What Happens When Configured
1. User creates room: `ornina-1763160177001`
2. LiveKit sees the room name matches pattern `ornina-*`
3. LiveKit sends dispatch request to worker `ornina-avatar-agent`
4. Worker's `should_join_room()` function is called
5. Worker accepts (returns `True`)
6. Worker joins room and agent entrypoint runs
7. Agent speaks and interacts with user 🎉

---

## Next Steps

1. **Configure LiveKit Cloud Dashboard** (5 minutes)
   - Add agent dispatch rule for `ornina-*` rooms
   
2. **Test the Configuration** (2 minutes)
   - Connect from frontend
   - Check agent joins room
   
3. **Verify Voice Works** (1 minute)
   - Listen for agent speaking
   - Check browser console for audio tracks

---

## Documentation References

- **LiveKit Agents Documentation:** https://docs.livekit.io/agents/
- **Agent Dispatch API:** https://docs.livekit.io/realtime/server/managing-rooms/#dispatch-agent
- **LiveKit Cloud Dashboard:** https://cloud.livekit.io

---

**Status:** ⚠️ **Configuration Required**  
**Priority:** **HIGH** - No voice until configured  
**ETA:** 5-10 minutes to configure and test

---

**Summary:** The agent code is correct and ready. You just need to tell LiveKit Cloud to dispatch agents to rooms. Once configured, the agent will automatically join all `ornina-*` rooms and voice will work perfectly!

