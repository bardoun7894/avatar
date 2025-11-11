# Quick Fix Reference - Voice Response Issue

## The Problem
Microphone is open and customer can talk, BUT no voice response from AI agent.

## Root Cause
**Line 105 in `/var/www/avatar/callCenter/call_center_agent.py`**

The VoiceAssistant is not being created correctly, preventing the entire voice pipeline from functioning.

## The Bug
```python
# WRONG (Line 105):
assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)
```

## The Fix
```python
# CORRECT:
from livekit.agents import VoiceAssistant

assistant = VoiceAssistant.create(
    ctx=ctx,
    options=opts,
    initial_ctx=initial_ctx
)
```

## Secondary Issues

### Issue 2: TTS Voice (Line 98)
- Currently uses `voice="alloy"` for all languages
- Should be language-aware:
```python
voice="nova"  # For both AR and EN (better support)
# OR
voice="alloy" if language == "en" else "nova"
```

### Issue 3: Missing Error Handling (Lines 107-109)
Add try-catch:
```python
try:
    logger.info("🎙️ Starting voice assistant...")
    await assistant.start()
except Exception as e:
    logger.error(f"Failed to start voice assistant: {e}")
    raise
```

## Pipeline Status Check

1. ✅ **Microphone Input** - Working
2. ✅ **STT (Speech-to-Text)** - Working  
3. ✅ **LLM (Response Generation)** - Working
4. ❌ **TTS (Text-to-Speech)** - BROKEN (due to Line 105)
5. ❌ **Audio Output** - Broken (caused by #4)

## How to Verify Fix

After fixing Line 105:
1. Restart agent container: `docker restart avatar-backend`
2. Check logs: `docker logs avatar-backend`
3. Look for: "Starting voice assistant..." log message
4. Test call: Customer should hear agent voice response

## Files Involved

| File | Line | Issue | Fix Priority |
|------|------|-------|--------------|
| call_center_agent.py | 105 | VoiceAssistant creation | CRITICAL |
| call_center_agent.py | 98 | TTS voice hardcoded | HIGH |
| call_center_agent.py | 109 | No error handling | HIGH |
| audio_handler.py | 81-133 | Not integrated with agent | MEDIUM |
| config.py | N/A | No voice config | MEDIUM |

## Testing Checklist

- [ ] Fix Line 105 (VoiceAssistant.create)
- [ ] Fix Line 98 (Language-aware TTS voice)
- [ ] Add error handling to Line 109
- [ ] Restart agent container
- [ ] Check agent logs for "Starting voice assistant..."
- [ ] Place test call
- [ ] Verify agent voice response heard

## Container Commands

```bash
# Restart agent
docker restart avatar-backend

# View logs
docker logs -f avatar-backend

# View call center API logs
docker logs -f avatar-callcenter
```

## Expected Audio Flow After Fix

```
Customer: "Hello" (microphone)
    ↓
Whisper STT: "Hello" (text)
    ↓
GPT-4 LLM: "Hello! Welcome to..." (response text)
    ↓
OpenAI TTS: Audio synthesis (bytes)
    ↓
LiveKit: Audio stream to customer
    ↓
Customer: Hears agent voice response (working!)
```
