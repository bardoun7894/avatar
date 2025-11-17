# Switch to Your Other LiveKit Project

## Current Situation

**Problem:** Tavus LiveKit project (`tavus-agent-project-i82x78jc`) doesn't support agent dispatch API or has conflicts with Tavus's default agent.

**Solution:** Use your OTHER LiveKit project (call center) which likely has proper agent dispatch configuration!

---

## What You Need

From your **other LiveKit project**, get:

1. **LiveKit URL** (wss://your-project.livekit.cloud or self-hosted URL)
2. **API Key**
3. **API Secret**

---

## How to Switch

### Step 1: Update Backend Environment

Edit `.env.production`:

```bash
# Change from Tavus project to your call center project
LIVEKIT_URL=wss://YOUR-OTHER-PROJECT.livekit.cloud
LIVEKIT_API_KEY=YOUR_OTHER_API_KEY
LIVEKIT_API_SECRET=YOUR_OTHER_API_SECRET

# Keep your existing configs
OPENAI_API_KEY=sk-proj-dOlBZCmL3WWJ...
ELEVENLABS_API_KEY=sk_8486e31b70b9f98...
TAVUS_API_KEY=1683bc5e621a49a287c3c558909e7f4b
TAVUS_REPLICA_ID=rca8a38779a8
TAVUS_PERSONA_ID=pa9c7a69d551
```

### Step 2: Update Frontend Environment

Edit `frontend/.env.production`:

```bash
# Change LiveKit URL
NEXT_PUBLIC_LIVEKIT_URL=wss://YOUR-OTHER-PROJECT.livekit.cloud
NEXT_PUBLIC_CALLCENTER_LIVEKIT_URL=wss://YOUR-OTHER-PROJECT.livekit.cloud

# Update API credentials
LIVEKIT_API_KEY=YOUR_OTHER_API_KEY
LIVEKIT_API_SECRET=YOUR_OTHER_API_SECRET
```

### Step 3: Rebuild and Restart

```bash
cd /var/www/avatar

# Rebuild both services
docker-compose -f docker-compose.prod.yml build backend frontend

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

---

## Why This Will Work

Your other LiveKit project likely:

✅ **Has agent dispatch properly configured**  
✅ **Doesn't have Tavus conflicts** (it's a separate project)  
✅ **Supports explicit agent dispatch API**  
✅ **Already working for call center**  

---

## What Will Happen

1. **Agent worker** connects to your other LiveKit project
2. **Registers** with agent name `ornina-avatar-agent`
3. **Frontend** dispatches to the same project
4. **No Tavus conflicts** (different project)
5. **Agent joins rooms** successfully
6. **Voice works!** 🎉

---

## Optional: Use Tavus Only for Video

If you still want Tavus video avatar, you can:

1. Use your **other LiveKit project** for the agent worker
2. Configure **Tavus** to use the same LiveKit project
3. Or use Tavus **only for video overlay** (not agent)

---

## Quick Test

After switching:

```bash
# Check agent connects to new project
docker logs avatar-backend --tail 50

# Should see:
# registered worker
# url: wss://YOUR-OTHER-PROJECT.livekit.cloud

# Test dispatch
curl -X POST http://localhost:3000/api/dispatch-agent \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test-new-project"}'
```

---

## Your Choice

**Option A: Use Other LiveKit Project** (Recommended)
- Switch everything to your call center project
- Agent dispatch will work immediately
- No Tavus conflicts

**Option B: Fix Current Tavus Project**
- Configure LiveKit Cloud dashboard
- Add agent dispatch rules
- Deal with Tavus default agent conflict

**Option C: Self-Host LiveKit Server**
- Run your own LiveKit server
- Full control over agent dispatch
- No cloud limitations

---

## What I Need From You

Can you provide the credentials for your **other LiveKit project**?

1. LiveKit URL: `wss://???`
2. API Key: `???`
3. API Secret: `???`

Once you provide these, I'll update the configuration immediately!

---

**This is likely the quickest path to getting voice working!** 🚀

