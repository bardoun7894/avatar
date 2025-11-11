# Audio/Voice Pipeline Analysis - Call Center System

## Summary
The call center application has a **broken audio/voice response pipeline**. Signal is detected (customer can talk) but the AI agent never responds with voice output. The root causes are multiple critical failures in the voice synthesis and streaming chain.

---

## 1. AUDIO/VOICE PIPELINE ARCHITECTURE

### Current Flow (Intended):
```
Customer Audio Input (Microphone)
    ↓
LiveKit Room (Audio Capture)
    ↓
STT (Speech-to-Text) via OpenAI Whisper
    ↓
LLM (Language Model) via OpenAI GPT
    ↓
TTS (Text-to-Speech) via OpenAI TTS
    ↓
Audio Output (Speaker/Headphones)
```

### The Pipeline Components:

#### A. **Speech-to-Text (STT) - WORKING**
- Location: `/var/www/avatar/callCenter/call_center_agent.py` (Line 96)
- Implementation: OpenAI Whisper-1 model
- Status: Operating correctly - transcription is working
- Code:
```python
transcription=openai.STT(model="whisper-1"),
```

#### B. **Language Model (LLM) - WORKING**
- Location: `/var/www/avatar/callCenter/call_center_agent.py` (Line 97)
- Implementation: OpenAI GPT-4-turbo-preview
- Status: Operating correctly - responses are generated
- Code:
```python
chat=openai.LLM(model="gpt-4-turbo-preview"),
```

#### C. **Text-to-Speech (TTS) - CRITICAL FAILURE #1**
- Location: `/var/www/avatar/callCenter/call_center_agent.py` (Line 98)
- Implementation: OpenAI TTS model
- Status: **BROKEN**
- Issues:
  1. Using deprecated `tts-1` model (should be `tts-1-hd` for quality)
  2. Using `alloy` voice for Arabic (wrong voice - alloy is English-optimized)
  3. No fallback mechanism if TTS fails
  4. No error handling for synthesis failures

```python
tts=openai.TTS(model="tts-1", voice="alloy"),
```

#### D. **Voice Assistant Creation - CRITICAL FAILURE #2**
- Location: `/var/www/avatar/callCenter/call_center_agent.py` (Line 105)
- Status: **BROKEN - API MISUSE**
- Issue: Incorrect API call signature
- Current Code (WRONG):
```python
assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)
```

- Correct Signature Should Be:
```python
# Should use VoiceAssistant.create() not VoiceAssistantOptions.create()
assistant = agents.VoiceAssistant.create(
    ctx=ctx,
    options=opts,
    initial_ctx=initial_ctx
)
```

**This is the PRIMARY cause of voice response failure.** The `VoiceAssistantOptions.create()` method doesn't exist as called - it's attempting to instantiate options as if it were the assistant itself.

---

## 2. WHERE THE BREAK IN THE CHAIN IS

### Primary Break Point: **Line 105 in call_center_agent.py**

The critical error is calling a non-existent method:
- `VoiceAssistantOptions.create()` is NOT a valid factory method
- Should be: `agents.VoiceAssistant.create()`
- Result: Voice assistant never properly initializes
- Impact: Agent joins room but cannot process audio through the full pipeline

### Secondary Break Points:

1. **Line 98 - TTS Configuration Issues:**
   - `voice="alloy"` is for English, not Arabic
   - Should auto-detect language and use appropriate voice:
     ```python
     voice="nova" if language == "en" else "alloy"
     ```

2. **No Fallback TTS:**
   - `/var/www/avatar/callCenter/audio_handler.py` has TTS capabilities
   - But NOT integrated into the LiveKit agent pipeline
   - Fallback to ElevenLabs available but not connected

3. **Missing Error Handling:**
   - No try-catch around `assistant.start()`
   - No logging of initialization failures
   - Agent crashes silently without clear error messages

---

## 3. SPECIFIC FILES AND LINE NUMBERS TO CHECK

### Critical File #1: `/var/www/avatar/callCenter/call_center_agent.py`

| Line | Issue | Severity | Fix |
|------|-------|----------|-----|
| 13 | Wrong import - missing `agents` module usage | CRITICAL | Import `agents` properly |
| 96-103 | VoiceAssistantOptions configuration | HIGH | Configuration is correct but method call is wrong |
| 105 | **MAIN BUG**: Wrong method call `VoiceAssistantOptions.create()` | CRITICAL | Use `agents.VoiceAssistant.create()` |
| 98 | TTS voice hardcoded to `alloy` for all languages | HIGH | Make voice language-aware |
| 109 | `await assistant.start()` fails due to Line 105 error | CRITICAL | Fix Line 105 first |

### Critical File #2: `/var/www/avatar/callCenter/audio_handler.py`

| Line | Issue | Severity |
|------|-------|----------|
| 81-133 | TTS synthesis function exists but NOT called from agent | HIGH |
| 25 | OpenAI client initialized for TTS | OK | But not used in agent pipeline |
| 98-100 | Mock fallback only returns empty bytes | MEDIUM | Should provide actual TTS fallback |

### Related Files:

- `/var/www/avatar/callCenter/api.py` (Lines 117-124): Audio endpoints registered but not connected to agent
- `/var/www/avatar/callCenter/livekit_endpoints.py`: Token generation OK, room management OK
- `/var/www/avatar/callCenter/conversation_manager.py`: LLM response generation works, but no TTS integration

---

## 4. CONFIGURATION ISSUES

### Environment Variables - `.env`

**REQUIRED for Voice Output (Currently Present):**
- ✅ `OPENAI_API_KEY` - Present and valid
- ✅ `LIVEKIT_URL` - Points to `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- ✅ `LIVEKIT_API_KEY` - Present
- ✅ `LIVEKIT_API_SECRET` - Present
- ✅ `ELEVENLABS_API_KEY` - Present (but not used)

**MISSING Configuration:**
- ❌ No TTS model preference specified
- ❌ No voice mapping for Arabic
- ❌ No fallback TTS service designation
- ❌ No audio output format specification (should be MP3 for compatibility)

### Configuration File: `/var/www/avatar/callCenter/config.py`

**Missing Voice Output Configuration:**
```python
# These should be added:
TTS_MODEL = "tts-1-hd"  # Higher quality
TTS_VOICE_MAP = {
    "ar": "nova",  # Arabic voice
    "en": "nova",  # English voice
}
FALLBACK_TTS_SERVICE = "elevenlabs"
AUDIO_OUTPUT_FORMAT = "mp3"
```

---

## 5. WHAT PREVENTS VOICE RESPONSE

### Root Cause Chain:

1. **Agent joins LiveKit room** ✓ (Working)
2. **Customer talks** ✓ (Microphone open, signal detected)
3. **STT processes audio** ✓ (Whisper model converts to text)
4. **LLM generates response** ✓ (GPT-4 returns text)
5. **TTS supposed to synthesize voice** ✗ **FAILS HERE**
   - Reason: VoiceAssistant never properly initialized (Line 105)
   - Agent code crashes/hangs at initialization
   - TTS module never receives text to synthesize

6. **Audio never streamed back** ✗ (No voice output)
   - Agent doesn't send audio frames to LiveKit room
   - Customer hears silence

### The Symptom:
- Microphone open and working (upstream part of pipeline)
- No voice response (downstream part broken)
- This matches exactly what user reported

---

## 6. DOCKER CONTAINERS

The system runs in Docker:

**Container Name:** `avatar-callcenter` (FastAPI server)
- Status: Running
- Port: 8000
- Serving REST/WebSocket endpoints
- Audio endpoints registered but not utilized

**Container Name:** `avatar-backend` (LiveKit Agent)
- Status: Running  
- Runs: `python agent.py start`
- This is where call_center_agent.py runs
- **This container's agent fails to initialize voice assistant**

---

## SOLUTION SUMMARY

To fix the voice pipeline:

### Immediate Fix (Critical - Line 105):
```python
# WRONG (Current):
assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)

# CORRECT:
from livekit.agents import VoiceAssistant
assistant = VoiceAssistant.create(
    ctx=ctx,
    options=opts,
    initial_ctx=initial_ctx
)
```

### Secondary Fixes:
1. Make TTS voice language-aware (Line 98)
2. Add error handling around `assistant.start()` (Line 109)
3. Add fallback TTS to audio_handler if OpenAI fails
4. Update config.py with voice/language mappings
5. Add logging to track TTS failures

### Verification Steps:
1. Check agent logs for voice synthesis errors
2. Verify VoiceAssistant initialization completes
3. Test TTS with sample text
4. Verify audio frames reach LiveKit room
5. Check customer receives voice output

---

## KEY FILES SUMMARY

| File | Purpose | Voice Support | Status |
|------|---------|----------------|--------|
| call_center_agent.py | Main agent logic | STT/LLM/TTS config | BROKEN - Line 105 |
| audio_handler.py | TTS/transcription | TTS synthesis | UNUSED |
| api.py | REST endpoints | Audio endpoints | Registered but unused |
| conversation_manager.py | LLM responses | Text generation only | INCOMPLETE |
| config.py | Configuration | No voice config | MISSING |
| livekit_manager.py | Room tokens | OK | WORKING |

