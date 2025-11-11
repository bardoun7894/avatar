# Call Center Configuration Analysis

## Executive Summary

This document explains the current configuration of the Call Center system and how to make it work like the Avatary system (which is already working).

**Status:**
- ✅ **Avatary (Video Avatar):** Fully working
- ⚠️  **Call Center (Audio Multi-Assistant):** API working, but LiveKit agent worker NOT started

---

## System Architecture

### Two Backend Systems

```
/var/www/avatar/
├── avatary/              ← Video Avatar Backend (WORKING)
│   ├── agent.py         ← LiveKit Agent Worker (runs on startup)
│   ├── .env             ← Configuration
│   └── Dockerfile       ← CMD: python agent.py start
│
├── callCenter/          ← Audio Call Center Backend (NEEDS FIX)
│   ├── api.py           ← FastAPI Server (RUNNING ✅)
│   ├── main.py          ← Starts FastAPI only
│   ├── call_center_agent.py  ← LiveKit Agent Worker (NOT STARTED ❌)
│   ├── openai_personas.py    ← 3 Personas: Reception, Sales, Complaints
│   ├── .env             ← Configuration (same credentials as avatary)
│   └── Dockerfile       ← CMD: python main.py (only starts API!)
│
└── frontend/            ← Shared Next.js Frontend
    ├── pages/callcenter/*    ← Call Center UI
    └── pages/avatar/*        ← Avatar UI
```

---

## How Avatary Works (Reference)

### Avatary Startup Process

1. **Docker Container Starts:**
   ```bash
   CMD ["python", "agent.py", "start"]
   ```

2. **agent.py Initialization:**
   ```python
   # agent.py creates a LiveKit Agent Worker
   from livekit import agents

   # Worker connects to LiveKit Cloud
   agents.Worker(
       url=LIVEKIT_URL,  # wss://tavus-agent-project-i82x78jc.livekit.cloud
       api_key=LIVEKIT_API_KEY,
       api_secret=LIVEKIT_API_SECRET
   )
   ```

3. **Agent Connects:**
   - Worker listens for room join requests
   - When user joins room, agent auto-joins
   - Agent handles: STT → LLM → TTS pipeline
   - Optional: Tavus video avatar overlay

4. **Result:**
   - Single process handles everything
   - Works with or without video (audio fallback)
   - User gets real-time voice conversation

---

## How Call Center Currently Works

### Current Setup (API Only)

1. **Docker Container Starts:**
   ```bash
   CMD ["python", "main.py"]
   ```

2. **main.py Only Starts FastAPI:**
   ```python
   # main.py
   uvicorn.run("api:app", host="0.0.0.0", port=8000)
   ```

3. **What's Running:**
   - ✅ FastAPI API Server (port 8000)
   - ✅ Token generation endpoints
   - ✅ CRM system API
   - ✅ Call routing logic
   - ❌ **LiveKit Agent Worker** (NOT RUNNING!)

4. **Problem:**
   - Frontend requests token → ✅ Works
   - Frontend joins room → ✅ Works
   - **Agent should auto-join room → ❌ DOESN'T HAPPEN**
   - User sits in empty room with no voice response

---

## The Missing Piece

### What's NOT Running

**File:** `callCenter/call_center_agent.py`

This file exists and contains:
- LiveKit Agent Worker code
- OpenAI STT/LLM/TTS integration
- System prompts
- Voice Assistant setup

**But it's never executed!**

The Dockerfile only runs `main.py` which starts the API server. The agent worker is a **separate process** that needs to be started independently.

---

## Configuration Comparison

### Avatary .env (Working)

```bash
# LiveKit Cloud
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud

# Tavus (Video Avatar)
TAVUS_API_KEY=457fcf2b5d734c34bbb88c8f55c1de60
TAVUS_PERSONA_ID=pa9c7a69d551
TAVUS_REPLICA_ID=rca8a38779a8

# OpenAI (Fallback)
OPENAI_API_KEY=sk-proj-dOlBZCmL...

# ElevenLabs (Arabic Voice)
ELEVENLABS_API_KEY=sk_8486e31b70b9f98...
ELEVENLABS_VOICE_ID=nH7M8bGCLQbKoS0wBZj7

# Avatar Mode
AVATAR_PROVIDER=tavus  # or audio, none, hedra
```

### Call Center .env (Has All Credentials)

```bash
# LiveKit Cloud (SAME AS AVATARY)
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA

# OpenAI (SAME AS AVATARY)
OPENAI_API_KEY=sk-proj-dOlBZCmL...

# ElevenLabs (SAME AS AVATARY)
ELEVENLABS_API_KEY=sk_8486e31b70b9f98...
ELEVENLABS_VOICE_ID=nH7M8bGCLQbKoS0wBZj7

# Call Center Specific
CALL_CENTER_MODE=enabled
DEFAULT_LANGUAGE=ar
```

**✅ Call Center has all the same credentials as Avatary!**

---

## Multi-Assistant System (Ready But Not Used)

### File: `callCenter/openai_personas.py`

This file defines **3 distinct AI personas:**

#### 1. Reception Persona (Ahmed)
```python
name="Ahmed"
department="Reception"
tone="Friendly, helpful, professional"

system_prompt="""
أنت أحمد، موظف استقبال ودود واحترافي في شركة أورنينا.
You are Ahmed, a friendly reception agent for Ornina company.

Your role:
- Greet customers warmly
- Collect basic information (name, phone, email, service type)
- Provide company information
- Route to appropriate department
"""
```

#### 2. Sales Persona (Sarah)
```python
name="Sarah"
department="Sales"
tone="Enthusiastic, professional, persuasive"

system_prompt="""
أنت سارة، ممثلة مبيعات متحمسة في شركة أورنينا.
You are Sarah, an enthusiastic sales representative.

Your role:
- Explain services with enthusiasm
- Handle objections
- Provide quotes
- Close deals
"""
```

#### 3. Complaints Persona (Mohammed)
```python
name="Mohammed"
department="Complaints & Support"
tone="Empathetic, professional, solution-focused"

system_prompt="""
أنت محمد، متخصص شكاوى متعاطف في شركة أورنينا.
You are Mohammed, an empathetic complaints specialist.

Your role:
- Listen carefully
- Show genuine empathy
- Propose solutions
- Create support tickets
"""
```

### Usage in Code

```python
from openai_personas import get_persona_manager

# Get persona manager
manager = get_persona_manager()

# Get system prompt for current persona
system_prompt = manager.get_system_prompt(
    PersonaType.RECEPTION,  # or SALES, COMPLAINTS
    language="ar"           # or "en"
)

# Switch persona during call
manager.set_current_persona(PersonaType.SALES)
```

**✅ Multi-assistant system is implemented and ready to use!**

---

## How to Make Call Center Work

### Solution 1: Start Agent Worker Manually (Quick Test)

```bash
# Terminal 1: Start API Server
cd /var/www/avatar/callCenter
python main.py

# Terminal 2: Start Agent Worker
cd /var/www/avatar/callCenter
python call_center_agent.py
```

### Solution 2: Update Dockerfile (Production)

**Current Dockerfile:**
```dockerfile
CMD ["python", "main.py"]
```

**Updated Dockerfile (Option A - Supervisor):**
```dockerfile
# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

**supervisord.conf:**
```ini
[supervisord]
nodaemon=true

[program:api]
command=python main.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/logs/api.log
stderr_logfile=/app/logs/api_error.log

[program:agent]
command=python call_center_agent.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/logs/agent.log
stderr_logfile=/app/logs/agent_error.log
```

**Updated Dockerfile (Option B - Shell Script):**
```dockerfile
# Copy startup script
COPY start_all.sh /app/start_all.sh
RUN chmod +x /app/start_all.sh

# Run both processes
CMD ["/app/start_all.sh"]
```

**start_all.sh:**
```bash
#!/bin/bash

# Start API server in background
python main.py &
API_PID=$!

# Start agent worker in background
python call_center_agent.py &
AGENT_PID=$!

# Wait for both processes
wait $API_PID $AGENT_PID
```

### Solution 3: Separate Docker Services (Recommended)

**Update docker-compose.yml:**
```yaml
services:
  # Call Center API
  callcenter-api:
    build: ./callCenter
    container_name: avatar-callcenter-api
    command: python main.py
    ports:
      - "8000:8000"
    env_file: ./callCenter/.env

  # Call Center Agent Worker
  callcenter-agent:
    build: ./callCenter
    container_name: avatar-callcenter-agent
    command: python call_center_agent.py
    env_file: ./callCenter/.env
    depends_on:
      - callcenter-api
```

---

## Integration with Multi-Assistant

### Current call_center_agent.py (Single Persona)

```python
# Current code - single static prompt
CALL_CENTER_SYSTEM_PROMPT = """
أنت مساعد استقبال آلي احترافي في مركز الاتصالات.
You are a professional automated receptionist...
"""

initial_ctx = llm.ChatContext().add_messages(
    llm.ChatMessage(role="system", content=CALL_CENTER_SYSTEM_PROMPT),
)
```

### Updated call_center_agent.py (Multi-Assistant)

```python
from openai_personas import get_persona_manager, PersonaType

# Get persona manager
persona_manager = get_persona_manager()

# Determine persona based on call routing
# This info should come from call_router or API
current_department = "reception"  # from call metadata

# Map department to persona
persona_map = {
    "reception": PersonaType.RECEPTION,
    "sales": PersonaType.SALES,
    "complaints": PersonaType.COMPLAINTS
}

persona_type = persona_map.get(current_department, PersonaType.RECEPTION)

# Get appropriate system prompt
system_prompt = persona_manager.get_system_prompt(
    persona_type,
    language="ar"  # or detect from user
)

# Create context with correct persona
initial_ctx = llm.ChatContext().add_messages(
    llm.ChatMessage(role="system", content=system_prompt),
)

# Create assistant
assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)
```

### Dynamic Persona Switching

```python
# During call, when transferring to another department
async def transfer_call(new_department: str):
    # Get new persona
    new_persona = persona_map[new_department]
    persona_manager.set_current_persona(new_persona)

    # Get new system prompt
    new_prompt = persona_manager.get_system_prompt(
        new_persona,
        language="ar"
    )

    # Update LLM context
    # (Implementation depends on LiveKit API for context updates)
    await assistant.update_system_prompt(new_prompt)
```

---

## Testing Checklist

### ✅ Avatary (Working)
- [x] LiveKit Agent Worker starts automatically
- [x] Agent joins room when user connects
- [x] STT/LLM/TTS pipeline works
- [x] Arabic voice (ElevenLabs) works
- [x] Video avatar (Tavus) works or falls back to audio
- [x] Conversation logging works

### ⚠️ Call Center (Needs Fix)
- [x] FastAPI server starts
- [x] Token generation works
- [x] CRM endpoints work
- [x] Credentials configured correctly
- [x] Personas defined (Reception, Sales, Complaints)
- [ ] **LiveKit Agent Worker starts** ← MISSING
- [ ] **Agent joins room automatically** ← MISSING
- [ ] **Multi-assistant switching works** ← NOT IMPLEMENTED

---

## Next Steps

### Immediate (Make It Work)

1. **Start Agent Worker:**
   ```bash
   cd /var/www/avatar/callCenter
   python call_center_agent.py
   ```

2. **Test Call Flow:**
   - Open frontend: http://localhost:3000/callcenter/call-with-audio
   - Check if agent joins automatically
   - Speak and verify voice response

### Short Term (Production Setup)

1. **Update Dockerfile:** Use supervisor or separate services
2. **Test persona switching:** Implement transfer logic
3. **Add logging:** Track persona changes and transfers
4. **Monitor both processes:** Ensure both API and agent stay running

### Long Term (Enhancements)

1. **Smart Routing:** Auto-detect department from user intent
2. **Persona Context:** Share CRM data between personas
3. **Handoff Protocol:** Smooth transfers with context
4. **Analytics:** Track performance per persona

---

## Key Differences: Avatary vs Call Center

| Feature | Avatary | Call Center |
|---------|---------|-------------|
| **Purpose** | Video avatar calls | Audio-only support calls |
| **Video** | Yes (Tavus) | No (audio only) |
| **Personas** | Single agent | 3 personas (Reception, Sales, Complaints) |
| **Startup** | Single process (agent.py) | Two processes (API + Agent) |
| **Port** | 8080 | 8000 (API), agent connects to LiveKit |
| **Architecture** | Simple | Complex (CRM, routing, tickets) |
| **Status** | ✅ Working | ⚠️ Partially working (agent not started) |

---

## Configuration Summary

### Both Systems Use Same Cloud Infrastructure

```
Production LiveKit Server:
wss://tavus-agent-project-i82x78jc.livekit.cloud

├── Avatary Rooms
│   └── Agent: avatary/agent.py
│       └── Mode: Video (Tavus) or Audio (ElevenLabs)
│
└── Call Center Rooms
    └── Agent: callCenter/call_center_agent.py (NOT STARTED!)
        └── Mode: Audio only (OpenAI + ElevenLabs)
        └── Personas: Reception → Sales → Complaints
```

**Both can run simultaneously - no conflicts!**

---

## Conclusion

### The Solution is Simple

**Call Center has everything it needs:**
- ✅ Correct LiveKit credentials
- ✅ OpenAI API key
- ✅ ElevenLabs for Arabic voice
- ✅ Multi-assistant personas defined
- ✅ LiveKit agent code ready (`call_center_agent.py`)

**Just one thing missing:**
- ❌ The agent worker is not being started!

**To fix:**
1. Start `call_center_agent.py` alongside `main.py`
2. Integrate `openai_personas.py` into the agent
3. Implement persona switching during call transfers

**Then call center will work exactly like avatary, but with:**
- Audio-only (no video)
- 3 AI assistants instead of 1
- Smart routing between departments

---

**Document Created:** 2025-11-10
**Author:** System Documentation
**Status:** Analysis Complete
