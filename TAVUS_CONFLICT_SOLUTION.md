# 🎯 TAVUS CONFLICT - The Real Issue Found!

## Discovery

Found in the documentation (`VISION_SYSTEM_FIX.md`):
> "User talked to AI and got responses, meaning **Tavus default system responded** (not our agent with vision)"

**THIS IS THE PROBLEM!**

## What's Happening

1. User connects to room: `ornina-1763160177001`
2. **Tavus's built-in agent automatically joins** (provides video avatar)
3. **Your custom agent worker never joins** (OpenAI voice, Arabic, knowledge base)
4. User talks to **Tavus's default agent** (generic responses, no custom voice)
5. That's why: ✅ Video works, ❌ Custom voice doesn't work

## The Conflict

**Two agents trying to handle the same room:**
- **Tavus Default Agent** ← Currently winning (joins automatically)
- **Your Custom Agent Worker** ← Never joins (no dispatch from LiveKit Cloud)

## Solutions

### Option 1: Make Custom Agent Join FIRST (Recommended)

Configure LiveKit Cloud to dispatch YOUR agent immediately when room is created:

1. **LiveKit Cloud Dashboard:**
   - Go to: https://cloud.livekit.io
   - Project: `tavus-agent-project-i82x78jc`
   - Settings → Agents
   - Create rule:
     ```
     Room Pattern: ornina-*
     Agent Name: ornina-avatar-agent
     Priority: HIGH
     Auto-dispatch: ON
     Dispatch Timing: IMMEDIATELY (on room creation)
     ```

2. **Disable Tavus Auto-Join** (if possible)
   - Check Tavus dashboard: https://tavus.io/dashboard
   - Look for "Auto-join" or "Default Agent" settings
   - Disable if found

### Option 2: Use Tavus API to Control Agent Behavior

Instead of relying on Tavus's default agent, explicitly create Tavus conversations via API:

**Modify agent entrypoint to:**
1. Join room FIRST
2. Then call Tavus API to attach video avatar to THIS agent
3. Prevent Tavus from auto-joining

```python
# In agent.py entrypoint
async def entrypoint(ctx: agents.JobContext):
    print("🚀 Custom agent joining room FIRST...")
    
    # Create Tavus conversation explicitly (controlled)
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://tavus.io/v2/conversations",
            headers={"x-api-key": os.environ.get("TAVUS_API_KEY")},
            json={
                "replica_id": os.environ.get("TAVUS_REPLICA_ID"),
                "persona_id": os.environ.get("TAVUS_PERSONA_ID"),
                "conversation_name": ctx.room.name,
                "properties": {
                    "livekit_room": ctx.room.name,
                    "custom_agent": True  # Prevent auto-join
                }
            }
        )
    
    # Continue with custom agent logic...
```

### Option 3: Change Agent Name to Match Tavus Expectation

The old docs mention `ornina-ai-agent`, but we're using `ornina-avatar-agent`. 

**Check what Tavus expects:**
```bash
# Query Tavus for configured agents
curl -X GET "https://tavus.io/v2/replicas/rca8a38779a8" \
  -H "x-api-key: 1683bc5e621a49a287c3c558909e7f4b"
```

## Quick Test: Disable Tavus Temporarily

To verify this is the issue, temporarily disable Tavus:

```bash
# Edit .env.production
AVATAR_PROVIDER=audio  # Change from 'tavus' to 'audio'
```

Then restart:
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

If your custom agent works WITHOUT Tavus, then the conflict is confirmed!

## Recommended Approach

1. **Keep Tavus video** (users want to see avatar)
2. **Use YOUR custom agent** (OpenAI voice, Arabic, knowledge base)
3. **Let Tavus handle video ONLY** (not conversation logic)

**Implementation:**
- Configure LiveKit to dispatch YOUR agent first
- Make Tavus video plugin attach to YOUR agent session
- Disable Tavus's conversational AI features

## Action Items

### Immediate (5 min):
- [ ] Check Tavus dashboard for auto-join settings
- [ ] Configure LiveKit Cloud agent dispatch rule
- [ ] Test with a new call

### If that doesn't work (15 min):
- [ ] Modify agent.py to explicitly control Tavus
- [ ] Use Tavus API to attach video to custom agent
- [ ] Test again

### Verification:
- [ ] Check logs for "NEW CONNECTION" from YOUR agent
- [ ] Hear Arabic voice from OpenAI (not Tavus default)
- [ ] See video avatar (Tavus video working)

---

**The key insight: Tavus is winning the race to join rooms. We need to either:**
1. Make YOUR agent faster/prioritized
2. Or disable Tavus's auto-join behavior

