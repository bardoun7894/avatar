# Detailed Code Fix Guide

## File: `/var/www/avatar/callCenter/call_center_agent.py`

### CRITICAL FIX #1: Line 105 - VoiceAssistant Creation

**Current Code (BROKEN):**
```python
    # Create voice assistant with streaming
    opts = VoiceAssistantOptions(
        transcription=openai.STT(model="whisper-1"),
        chat=openai.LLM(model="gpt-4-turbo-preview"),
        tts=openai.TTS(model="tts-1", voice="alloy"),
        # Use Silero VAD for voice activity detection
        vad=silero.VAD.load(),
        allow_interruptions=True,
        auto_reconnect=True,
    )

    # LINE 105 - THIS IS WRONG:
    assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)

    # Start processing audio
    logger.info("🎙️ Starting voice assistant...")
    await assistant.start()
```

**Fixed Code:**
```python
    # Create voice assistant with streaming
    opts = VoiceAssistantOptions(
        transcription=openai.STT(model="whisper-1"),
        chat=openai.LLM(model="gpt-4-turbo-preview"),
        tts=openai.TTS(model="tts-1", voice="nova"),  # Changed voice from alloy
        # Use Silero VAD for voice activity detection
        vad=silero.VAD.load(),
        allow_interruptions=True,
        auto_reconnect=True,
    )

    # LINE 105 - CORRECTED:
    from livekit.agents import VoiceAssistant  # Add this import at top of file
    
    assistant = VoiceAssistant.create(
        ctx=ctx,
        options=opts,
        initial_ctx=initial_ctx
    )

    # Start processing audio with error handling
    logger.info("🎙️ Starting voice assistant...")
    try:
        await assistant.start()
    except Exception as e:
        logger.error(f"Failed to start voice assistant: {e}")
        raise
```

---

### HIGH PRIORITY FIX #2: Line 98 - Language-Aware TTS Voice

**Current Code (NOT OPTIMIZED):**
```python
        tts=openai.TTS(model="tts-1", voice="alloy"),
```

**Fixed Code (Language-Aware):**
```python
        # Detect language from context or use default
        tts_voice = "nova"  # Best support for multiple languages
        if language and language.lower() in ["ar", "arabic"]:
            tts_voice = "nova"  # Nova handles Arabic well
        
        tts=openai.TTS(model="tts-1", voice=tts_voice),
```

---

### HIGH PRIORITY FIX #3: Lines 108-109 - Add Error Handling

**Current Code (NO ERROR HANDLING):**
```python
    # Start processing audio
    logger.info("🎙️ Starting voice assistant...")
    await assistant.start()

    # Keep agent alive while in room
    while ctx.room.is_connected:
```

**Fixed Code (WITH ERROR HANDLING):**
```python
    # Start processing audio
    logger.info("🎙️ Starting voice assistant...")
    try:
        await assistant.start()
    except Exception as e:
        logger.error(f"Voice assistant failed to start: {e}", exc_info=True)
        raise
    except asyncio.CancelledError:
        logger.info("Voice assistant startup cancelled")
        raise

    # Keep agent alive while in room
    while ctx.room.is_connected:
```

---

## Complete Fixed Function

Here's the complete corrected `entrypoint` function:

```python
async def entrypoint(ctx: AgentSession):
    """
    Main agent entrypoint - called when agent joins a room
    
    Args:
        ctx: The AgentSession context with room information
    """
    logger.info(f"📞 Agent joining room: {ctx.room.name}")
    logger.info(f"👥 Participants: {len(ctx.room.participants)}")

    # Detect language from room metadata or use default
    language = "ar"  # Default to Arabic for Ornina
    
    # Initialize conversation
    initial_ctx = llm.ChatContext().add_messages(
        llm.ChatMessage(
            role="system",
            content=CALL_CENTER_SYSTEM_PROMPT.format(
                current_time=asyncio.get_event_loop().time(),
                language=language,
                department="reception"
            ),
        ),
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        ),
    )

    # Select TTS voice based on language
    tts_voice = "nova"  # Nova works well for Arabic and English
    if language and language.lower() in ["en", "english"]:
        tts_voice = "nova"  # Use nova for English too
    
    # Create voice assistant with proper configuration
    opts = VoiceAssistantOptions(
        transcription=openai.STT(model="whisper-1"),
        chat=openai.LLM(model="gpt-4-turbo-preview"),
        tts=openai.TTS(model="tts-1", voice=tts_voice),
        # Use Silero VAD for voice activity detection
        vad=silero.VAD.load(),
        allow_interruptions=True,
        auto_reconnect=True,
    )

    # CRITICAL FIX: Use VoiceAssistant.create() not VoiceAssistantOptions.create()
    from livekit.agents import VoiceAssistant
    
    assistant = VoiceAssistant.create(
        ctx=ctx,
        options=opts,
        initial_ctx=initial_ctx
    )

    # Start processing audio with error handling
    logger.info("🎙️ Starting voice assistant...")
    try:
        await assistant.start()
    except Exception as e:
        logger.error(f"Failed to start voice assistant: {e}", exc_info=True)
        raise

    # Keep agent alive while in room
    while ctx.room.is_connected:
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("🛑 Agent shutting down...")
            break
        except Exception as e:
            logger.error(f"❌ Error in agent loop: {e}")
            await asyncio.sleep(1)

    logger.info("👋 Agent disconnected from room")
```

---

## File: `/var/www/avatar/callCenter/config.py`

### Add Voice Configuration (Around Line 440)

**Add this section:**
```python
# ============================================================================
# VOICE/TTS CONFIGURATION
# ============================================================================

# TTS Settings
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE_DEFAULT = "nova"  # Best for Arabic and English

# Voice mapping by language
TTS_VOICE_MAP = {
    "ar": "nova",      # Arabic
    "en": "nova",      # English
    "default": "nova"  # Fallback
}

# Audio output settings
AUDIO_OUTPUT_FORMAT = "mp3"
AUDIO_OUTPUT_SAMPLE_RATE = 24000

# Fallback TTS if OpenAI fails
FALLBACK_TTS_ENABLED = True
FALLBACK_TTS_SERVICE = "elevenlabs"  # Using ElevenLabs as fallback

# Voice activity detection
VAD_ENABLED = True
VAD_THRESHOLD = 0.5
```

---

## File: `/var/www/avatar/callCenter/.env`

### Ensure These Variables Are Set

Add/verify these in `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk_your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# TTS Settings
TTS_MODEL=tts-1
TTS_VOICE=nova

# Fallback Services
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=nH7M8bGCLQbKoS0wBZj7

# Audio Settings
AUDIO_OUTPUT_FORMAT=mp3
VAD_ENABLED=true
```

---

## Import Statement Fix

### At the top of `/var/www/avatar/callCenter/call_center_agent.py`

**Ensure proper imports:**
```python
#!/usr/bin/env python3
"""
Call Center LiveKit Agent
Automated agent for handling call center interactions with real-time STT/LLM/TTS
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentSession,
    VoiceAssistant,      # ADD THIS - Direct import of VoiceAssistant
    VoiceAssistantOptions,
    transcription,
    llm,
    tts
)
from livekit.plugins import openai, silero

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ... rest of file
```

---

## Step-by-Step Implementation

### Step 1: Update call_center_agent.py
1. Add `VoiceAssistant` import at top
2. Fix Line 105 (VoiceAssistant.create call)
3. Fix Line 98 (TTS voice)
4. Add error handling around Lines 108-109

### Step 2: Update config.py
1. Add voice configuration section

### Step 3: Update .env
1. Verify OPENAI_API_KEY is set
2. Verify TTS configuration variables

### Step 4: Restart Services
```bash
# Restart the agent container
docker restart avatar-backend

# Monitor logs
docker logs -f avatar-backend
```

### Step 5: Test
```bash
# Look for this log message:
# "🎙️ Starting voice assistant..."

# Then test a call
# Customer should hear agent voice
```

---

## Verification Checklist

After making changes:

- [ ] File `/var/www/avatar/callCenter/call_center_agent.py` updated
- [ ] Line 105 changed to `VoiceAssistant.create()`
- [ ] Line 98 TTS voice updated
- [ ] Error handling added to Line 109
- [ ] VoiceAssistant imported at top of file
- [ ] Config.py voice settings added
- [ ] Environment variables verified
- [ ] Docker container restarted
- [ ] Agent logs show "Starting voice assistant..."
- [ ] Test call: Customer hears agent response

