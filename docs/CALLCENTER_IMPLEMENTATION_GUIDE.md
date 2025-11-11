# Call Center Implementation Guide
## How to Make Call Center Work with Multi-Assistant Support

**Goal:** Make Call Center work like Avatary but with 3 AI assistants (Reception, Sales, Complaints) instead of 1.

---

## Quick Start (Test Mode)

### Step 1: Start Both Processes

```bash
# Terminal 1: API Server
cd /var/www/avatar/callCenter
source venv/bin/activate  # if using venv
python main.py
# → API running on http://localhost:8000

# Terminal 2: Agent Worker
cd /var/www/avatar/callCenter
source venv/bin/activate  # if using venv
python call_center_agent.py
# → Agent worker connecting to LiveKit...
```

### Step 2: Test the System

```bash
# Open browser
http://localhost:3000/callcenter/call-with-audio

# What should happen:
# 1. Frontend requests token from API (port 8000) ✅
# 2. Frontend joins LiveKit room ✅
# 3. Agent automatically joins room ✅
# 4. You hear welcome message ✅
# 5. Speak → AI responds ✅
```

---

## Production Setup (Docker)

### Option 1: Supervisor (Recommended)

**1. Install supervisor in Dockerfile:**

```dockerfile
# callCenter/Dockerfile
FROM python:3.11-slim

# Install system dependencies INCLUDING supervisor
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    ffmpeg \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Health check for API
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run supervisor to manage both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

**2. Create supervisor config:**

```ini
# callCenter/supervisord.conf
[supervisord]
nodaemon=true
logfile=/app/logs/supervisord.log
pidfile=/var/run/supervisord.pid

[program:api]
command=python main.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/logs/api.log
stderr_logfile=/app/logs/api_error.log
environment=PYTHONUNBUFFERED=1

[program:agent]
command=python call_center_agent.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/logs/agent.log
stderr_logfile=/app/logs/agent_error.log
environment=PYTHONUNBUFFERED=1
```

**3. Rebuild and test:**

```bash
docker-compose build callcenter
docker-compose up callcenter
```

### Option 2: Separate Docker Services (Best for Scaling)

**Update docker-compose.yml:**

```yaml
services:
  # Call Center API Server
  callcenter-api:
    build:
      context: ./callCenter
      dockerfile: Dockerfile
    container_name: avatar-callcenter-api
    restart: unless-stopped
    env_file:
      - ./callCenter/.env
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    volumes:
      - ./callCenter/logs:/app/logs
    ports:
      - "8000:8000"
    networks:
      - avatar-network
    depends_on:
      - redis
    command: python main.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Call Center Agent Worker
  callcenter-agent:
    build:
      context: ./callCenter
      dockerfile: Dockerfile
    container_name: avatar-callcenter-agent
    restart: unless-stopped
    env_file:
      - ./callCenter/.env
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    volumes:
      - ./callCenter/logs:/app/logs
    networks:
      - avatar-network
    depends_on:
      - callcenter-api
      - redis
    command: python call_center_agent.py
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Multi-Assistant Integration

### Step 1: Update call_center_agent.py

**Current code (single persona):**

```python
# call_center_agent.py (current - line 31-52)
CALL_CENTER_SYSTEM_PROMPT = """
أنت مساعد استقبال آلي احترافي في مركز الاتصالات.
You are a professional automated receptionist...
"""
```

**Updated code (multi-assistant):**

```python
# call_center_agent.py (updated)
from openai_personas import get_persona_manager, PersonaType

# Initialize persona manager
persona_manager = get_persona_manager()

def get_system_prompt(department: str = "reception", language: str = "ar") -> str:
    """Get system prompt based on department and language"""

    # Map department to persona
    persona_map = {
        "reception": PersonaType.RECEPTION,
        "sales": PersonaType.SALES,
        "complaints": PersonaType.COMPLAINTS
    }

    persona_type = persona_map.get(department, PersonaType.RECEPTION)

    # Get prompt from persona manager
    system_prompt = persona_manager.get_system_prompt(persona_type, language)

    # Add current time and context
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return system_prompt.format(
        current_time=current_time,
        language=language,
        department=department
    )


async def entrypoint(ctx: AgentSession):
    """Main agent entrypoint with multi-assistant support"""

    logger.info(f"📞 Agent joining room: {ctx.room.name}")

    # Extract department from room metadata (if provided)
    room_metadata = ctx.room.metadata or "{}"
    import json
    try:
        metadata = json.loads(room_metadata)
        department = metadata.get("department", "reception")
        language = metadata.get("language", "ar")
    except:
        department = "reception"
        language = "ar"

    logger.info(f"🎭 Starting with persona: {department}")

    # Get appropriate system prompt
    system_prompt = get_system_prompt(department, language)

    # Initialize conversation
    initial_ctx = llm.ChatContext().add_messages(
        llm.ChatMessage(role="system", content=system_prompt),
        llm.ChatMessage(
            role="assistant",
            content=get_welcome_message(department, language)
        ),
    )

    # Rest of the code remains the same...
    opts = VoiceAssistantOptions(...)
    assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)
    await assistant.start()
    # ...
```

### Step 2: Add Welcome Messages

```python
def get_welcome_message(department: str, language: str) -> str:
    """Get welcome message based on department and language"""

    messages = {
        "reception": {
            "ar": "أهلاً وسهلاً بكم في أورنينا. أنا أحمد، كيف يمكنني مساعدتك؟",
            "en": "Welcome to Ornina. I'm Ahmed, how can I help you today?"
        },
        "sales": {
            "ar": "مرحباً! أنا سارة من قسم المبيعات. سأساعدك في اختيار الخدمة المناسبة.",
            "en": "Hello! I'm Sarah from Sales. I'll help you choose the right service."
        },
        "complaints": {
            "ar": "أهلاً بك. أنا محمد من قسم الشكاوى. سأستمع لمشكلتك وأساعدك في حلها.",
            "en": "Welcome. I'm Mohammed from Complaints. I'll listen and help resolve your issue."
        }
    }

    return messages.get(department, messages["reception"]).get(language, messages["reception"]["ar"])
```

### Step 3: Update API to Pass Department

**In api.py (token generation endpoint):**

```python
# api.py - Update token generation endpoint
@app.post("/api/token")
async def get_token(request: TokenRequest):
    """Generate LiveKit token for call center room"""

    # ... existing token generation code ...

    # Add metadata to token
    metadata = {
        "department": request.department or "reception",
        "language": request.language or "ar",
        "customer_id": request.customer_id,
        "customer_name": request.customer_name
    }

    token = AccessToken(
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )

    token.add_grant(VideoGrant(
        room_join=True,
        room=room_name,
    ))

    # Set metadata
    token.metadata = json.dumps(metadata)

    # ... rest of code ...
```

---

## Persona Switching During Call

### Step 1: Add Transfer Capability

```python
# call_center_agent.py - Add transfer function
async def transfer_to_department(
    assistant,
    new_department: str,
    language: str = "ar"
):
    """Transfer call to different department (persona)"""

    logger.info(f"🔄 Transferring to {new_department}")

    # Get new persona
    new_prompt = get_system_prompt(new_department, language)

    # Announce transfer
    transfer_message = {
        "ar": f"جاري تحويلك إلى قسم {new_department}...",
        "en": f"Transferring you to {new_department} department..."
    }

    # Send transfer message
    await assistant.say(transfer_message[language])

    # Update system prompt (LiveKit API method)
    # Note: This depends on LiveKit version and API
    # May need to recreate assistant or update context
    await assistant.update_context(
        llm.ChatMessage(role="system", content=new_prompt)
    )

    # Send welcome from new department
    welcome = get_welcome_message(new_department, language)
    await assistant.say(welcome)

    logger.info(f"✅ Transferred to {new_department}")
```

### Step 2: Detect Transfer Intent

```python
# Add to entrypoint function
async def entrypoint(ctx: AgentSession):
    # ... initialization code ...

    # Listen for transfer requests
    @assistant.on("message")
    async def on_message(text: str):
        """Detect if user wants to transfer"""

        text_lower = text.lower()

        # Arabic transfer keywords
        if any(keyword in text_lower for keyword in ["مبيعات", "شراء", "عرض", "سعر"]):
            await transfer_to_department(assistant, "sales", language)

        elif any(keyword in text_lower for keyword in ["شكوى", "مشكلة", "تذمر", "complaint"]):
            await transfer_to_department(assistant, "complaints", language)

        # English transfer keywords
        elif any(keyword in text_lower for keyword in ["sales", "buy", "purchase", "price"]):
            await transfer_to_department(assistant, "sales", "en")

        elif any(keyword in text_lower for keyword in ["complaint", "problem", "issue"]):
            await transfer_to_department(assistant, "complaints", "en")

    await assistant.start()
    # ...
```

---

## Testing Multi-Assistant

### Test 1: Reception Persona

```bash
# Start call with reception
# User says: "مرحباً، أريد معلومات عن خدماتكم"
# Expected: Ahmed (reception) responds with company info
```

### Test 2: Transfer to Sales

```bash
# User says: "أريد شراء خدمة"
# Expected: System transfers to Sarah (sales)
# Sarah: "مرحباً! أنا سارة من قسم المبيعات..."
```

### Test 3: Transfer to Complaints

```bash
# User says: "لدي شكوى"
# Expected: System transfers to Mohammed (complaints)
# Mohammed: "أهلاً بك. أنا محمد من قسم الشكاوى..."
```

---

## Monitoring & Debugging

### Check Logs

```bash
# API logs
docker logs avatar-callcenter-api -f

# Agent logs
docker logs avatar-callcenter-agent -f

# Or with supervisor
docker exec -it avatar-callcenter tail -f /app/logs/api.log
docker exec -it avatar-callcenter tail -f /app/logs/agent.log
```

### Verify Agent Connection

```bash
# Check if agent connected to LiveKit
grep "Agent joining room" /var/www/avatar/callCenter/logs/agent.log

# Check persona switches
grep "Starting with persona" /var/www/avatar/callCenter/logs/agent.log
grep "Transferring to" /var/www/avatar/callCenter/logs/agent.log
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Token generation
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test", "department": "reception"}'
```

---

## Troubleshooting

### Problem: Agent doesn't join room

**Symptom:** User joins room but hears nothing

**Causes:**
1. Agent worker not running
2. Wrong LiveKit credentials
3. Network/firewall blocking WebSocket

**Solution:**
```bash
# Check agent is running
ps aux | grep call_center_agent

# Check LiveKit URL
echo $LIVEKIT_URL  # Should be: wss://tavus-agent-project-i82x78jc.livekit.cloud

# Test connection
curl -I https://tavus-agent-project-i82x78jc.livekit.cloud
```

### Problem: No voice response

**Symptom:** Agent joins but doesn't speak

**Causes:**
1. Missing OpenAI API key
2. Missing ElevenLabs key
3. TTS not configured

**Solution:**
```bash
# Check API keys
env | grep OPENAI_API_KEY
env | grep ELEVENLABS_API_KEY

# Check TTS configuration in call_center_agent.py
grep "tts=" call_center_agent.py
```

### Problem: Persona doesn't switch

**Symptom:** Always uses same persona

**Causes:**
1. Transfer logic not implemented
2. Department not passed in metadata
3. Message listener not registered

**Solution:**
- Follow "Persona Switching During Call" section above
- Verify metadata in token generation
- Add logging to detect transfer keywords

---

## Performance Optimization

### 1. Preload Models

```python
async def prewarm_plugins():
    """Preload TTS and STT plugins for faster responses"""
    logger.info("⚡ Prewarming plugins...")

    try:
        # Preload OpenAI STT
        await openai.STT(model="whisper-1").aclose()

        # Preload OpenAI TTS
        await openai.TTS(model="tts-1", voice="alloy").aclose()

        logger.info("✅ Plugins prewarmed")
    except Exception as e:
        logger.warning(f"⚠️ Prewarming failed: {e}")

# Call on startup
asyncio.run(prewarm_plugins())
```

### 2. Use Redis for Persona State

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def save_persona_state(room_name: str, department: str):
    """Save current persona for room"""
    redis_client.setex(f"persona:{room_name}", 3600, department)

def get_persona_state(room_name: str) -> str:
    """Get current persona for room"""
    persona = redis_client.get(f"persona:{room_name}")
    return persona.decode() if persona else "reception"
```

### 3. Optimize Response Time

```python
# Use streaming for faster responses
opts = VoiceAssistantOptions(
    transcription=openai.STT(model="whisper-1"),
    chat=openai.LLM(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=150  # Shorter responses = faster
    ),
    tts=openai.TTS(
        model="tts-1",  # Faster than tts-1-hd
        voice="alloy"
    ),
    vad=silero.VAD.load(),
    allow_interruptions=True,  # Allow user to interrupt
    auto_reconnect=True,
)
```

---

## Next Steps

1. ✅ Start agent worker (manual or Docker)
2. ✅ Test basic voice interaction
3. ⏳ Integrate multi-assistant (update call_center_agent.py)
4. ⏳ Add transfer detection
5. ⏳ Test all 3 personas
6. ⏳ Add logging and monitoring
7. ⏳ Deploy to production

---

## Summary

**What Was Missing:**
- Agent worker not running

**What You Have:**
- ✅ All credentials configured
- ✅ 3 personas defined (Reception, Sales, Complaints)
- ✅ LiveKit integration ready
- ✅ API server working

**What To Do:**
1. Start agent worker alongside API
2. Integrate personas into agent code
3. Add transfer logic for department switching

**Result:**
- Audio-only call center with 3 AI assistants
- Smart routing between Reception → Sales/Complaints
- Same infrastructure as Avatary (audio-only, no video)

---

**Document Created:** 2025-11-10
**Status:** Implementation Guide Complete
**Next:** Execute implementation steps
