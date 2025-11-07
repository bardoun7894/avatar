# Vision System Debugging Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Browser)                        │
│                  Camera + Microphone                         │
└──────────────────┬──────────────────────────────────────────┘
                   │ LiveKit WebRTC
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    LiveKit Room                              │
│  ┌────────────┐    ┌──────────┐    ┌───────────────────┐  │
│  │   User     │◄──►│  Agent   │◄──►│  Tavus Avatar     │  │
│  │  Tracks    │    │  Session │    │   (Video/Audio)   │  │
│  └────────────┘    └──────────┘    └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                   ▲
                   │
┌──────────────────┴──────────────────────────────────────────┐
│                  Backend Agent (agent.py)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vision Agent (vision_agent.py)                      │  │
│  │  - Monitors user video track                         │  │
│  │  - Captures frames every 5 seconds                   │  │
│  │  - Sends to GPT-4 Vision API                         │  │
│  │  - Returns Arabic description                        │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                              │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Context Manager (conversation_context_manager.py)   │  │
│  │  - Receives visual analysis                          │  │
│  │  - Updates Agent instructions via Pydantic           │  │
│  │  - Injects context before each response              │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                              │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LiveKit Agent                                       │  │
│  │  - Receives updated instructions                     │  │
│  │  - Generates responses via gpt-4o-mini               │  │
│  │  - Sends to Tavus Avatar                             │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                              │
│               ▼                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tavus Avatar Integration                            │  │
│  │  - Receives text from Agent                          │  │
│  │  - Converts to speech (TTS)                          │  │
│  │  - Sends video/audio to user                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Module Organization

### Core Modules

1. **agent.py** - Main orchestrator
   - Sets up LiveKit Agent Session
   - Registers tools
   - Manages conversation lifecycle

2. **vision_agent.py** - Vision processing
   - Monitors video tracks
   - Captures frames
   - Analyzes with GPT-4 Vision

3. **vision_processor.py** - Low-level frame capture
   - Converts LiveKit video frames
   - Manages memory efficiently
   - Handles JPEG encoding

4. **conversation_context_manager.py** - Context injection
   - Updates agent instructions dynamically
   - Manages visual context freshness
   - Uses Pydantic Agent.update_instructions()

5. **tavus_integration.py** - Tavus avatar API
   - Creates/manages Tavus conversations
   - Handles avatar lifecycle

## Debugging Steps

### 1. Check Vision Analysis is Working

```bash
tail -f /var/www/avatar\ /avatary/agent.log | grep "👁️"
```

**Expected output:**
```
👁️  Vision Agent: Analysis complete (234 chars)
👁️  Visual analysis: أرى شخصًا يجلس...
```

### 2. Check Instructions are Being Updated

```bash
tail -f /var/www/avatar\ /avatary/agent.log | grep "Agent instructions updated"
```

**Expected output:**
```
✅ Agent instructions updated with visual context via Pydantic model
```

### 3. Check Agent Responses

```bash
tail -f /var/www/avatar\ /avatary/agent.log | grep -E "user|assistant"
```

### 4. Full Diagnostic

```bash
python3 diagnostic_tool.py
```

## Common Issues

### Issue 1: Vision works but avatar doesn't acknowledge

**Symptoms:**
- ✅ Vision analysis shows correct descriptions
- ✅ Instructions updated
- ❌ Avatar doesn't mention what it sees

**Root Cause:**
Tavus Avatar may have its own instruction caching or the LiveKit Agent's updated instructions aren't being used for every turn.

**Solution:**
Instead of updating instructions, we need to inject visual context as a "system thought" or user message at the start of each conversation turn.

### Issue 2: Vision not starting

**Symptoms:**
- No "📹 Got user video track" messages
- No vision analysis logs

**Check:**
1. Camera permissions granted in browser
2. HTTPS connection (required for camera)
3. Video track is being published

### Issue 3: Memory leak

**Symptoms:**
- Process memory growing > 4GB
- Agent crashes

**Solution:**
- vision_processor.py properly closes streams
- JPEG quality reduced to 60%
- Analysis interval is 5 seconds

## Testing Visual Awareness

### Test Script

1. Connect to avatar
2. Hold up an object (book, phone, etc.)
3. Ask: "ماذا ترى؟" (What do you see?)
4. Avatar should describe the object

### Expected Behavior

Avatar should say something like:
> "أرى أنك تحمل هاتفًا في يدك" (I see you're holding a phone in your hand)

## Next Steps if Not Working

If visual context still isn't reaching responses:

1. **Try session.say() injection**
   - Inject as actual user message
   - Force avatar to "hear" the visual context

2. **Use conversation context**
   - Prepend visual context to each user message
   - Make it part of the conversation flow

3. **Custom Tavus API injection**
   - Use Tavus API to inject context directly
   - Update conversation metadata

## File Locations

- Main agent: `/var/www/avatar /avatary/agent.py`
- Vision logs: `/var/www/avatar /avatary/agent.log`
- Frontend logs: Browser console
- Configuration: `/var/www/avatar /avatary/.env`
