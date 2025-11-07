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
   - Creates VisualAwareAgent instance

2. **visual_aware_agent.py** ⭐ NEW - Custom Agent with context injection
   - Extends LiveKit Agent class
   - Overrides `llm_node` method (LiveKit Agents 1.0 pattern)
   - Injects visual context as system message before each LLM call
   - Uses Pydantic models for clean data management

3. **visual_context_models.py** ⭐ NEW - Pydantic models
   - `VisualAnalysis` - Single analysis with timestamp
   - `VisualContextStore` - Thread-safe context storage
   - Automatic freshness checking
   - Clean data validation

4. **vision_agent.py** - Vision processing
   - Monitors video tracks
   - Captures frames
   - Analyzes with GPT-4 Vision

5. **vision_processor.py** - Low-level frame capture
   - Converts LiveKit video frames
   - Manages memory efficiently
   - Handles JPEG encoding

6. **conversation_context_manager.py** - DEPRECATED
   - Old approach (updating instructions)
   - Kept for backward compatibility
   - Delegates to VisualAwareAgent methods

7. **tavus_integration.py** - Tavus avatar API
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

### Issue 1: Vision works but avatar doesn't acknowledge ✅ SOLVED

**Symptoms:**
- ✅ Vision analysis shows correct descriptions
- ✅ Instructions updated
- ❌ Avatar doesn't mention what it sees

**Root Cause:**
Tavus Avatar may have its own instruction caching or the LiveKit Agent's updated instructions aren't being used for every turn.

**Solution (IMPLEMENTED):**
✅ Created `VisualAwareAgent` class that overrides `llm_node` method
✅ Injects visual context as system message into ChatContext before EACH LLM call
✅ Uses LiveKit Agents 1.0 pattern (not deprecated `before_llm_cb`)
✅ Uses Pydantic models for clean data management

**How It Works:**
1. Vision processor analyzes frame → calls `agent.update_visual_context()`
2. Context stored in Pydantic `VisualContextStore`
3. When user speaks → `llm_node` called automatically
4. `llm_node` injects fresh visual context as system message
5. LLM receives context → generates response with visual awareness
6. Tavus avatar speaks response that acknowledges what it sees!

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

## Implementation Details (Current)

### Architecture Pattern: llm_node Override

The current implementation uses the **LiveKit Agents 1.0** pattern:

```python
class VisualAwareAgent(Agent):
    async def llm_node(self, chat_ctx, tools, model_settings):
        # Get fresh visual context from Pydantic store
        current_visual = self.visual_store.get_current()

        if current_visual and current_visual.is_fresh:
            # Inject as system message
            chat_ctx.add_message(
                role="system",
                content=current_visual.to_injection_text()
            )

        # Delegate to default LLM processing
        async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
            yield chunk
```

### Pydantic Models

**VisualAnalysis** - Represents a single vision analysis
```python
class VisualAnalysis(BaseModel):
    content: str  # Analysis text
    timestamp: datetime  # When created

    @property
    def is_fresh(self) -> bool:
        return self.age_seconds < 10
```

**VisualContextStore** - Thread-safe storage
```python
class VisualContextStore(BaseModel):
    latest_analysis: Optional[VisualAnalysis]
    max_age_seconds: float = 15.0
```

### Benefits of This Approach

1. ✅ **Reliable** - Context injected before EVERY LLM call
2. ✅ **Clean** - Uses Pydantic for type safety and validation
3. ✅ **Modern** - Uses LiveKit Agents 1.0 patterns (not deprecated APIs)
4. ✅ **Automatic** - No manual intervention needed
5. ✅ **Testable** - Easy to verify with `agent.get_visual_status()`

## Legacy Approaches (Not Recommended)

### ❌ Updating Instructions
Problem: Instructions may be cached by Tavus, not used every turn

### ❌ session.say() injection
Problem: Creates fake user messages, confuses conversation flow

### ❌ Prepending to user messages
Problem: Pollutes user input, hard to maintain

## File Locations

### Core Implementation
- Main agent: `/var/www/avatar /avatary/agent.py`
- Visual-aware agent: `/var/www/avatar /avatary/visual_aware_agent.py` ⭐ NEW
- Pydantic models: `/var/www/avatar /avatary/visual_context_models.py` ⭐ NEW
- Vision processor: `/var/www/avatar /avatary/vision_processor.py`
- Vision agent: `/var/www/avatar /avatary/vision_agent.py`

### Deprecated (backward compatibility)
- Context manager: `/var/www/avatar /avatary/conversation_context_manager.py` (use VisualAwareAgent instead)

### Configuration & Logs
- Vision logs: `/var/www/avatar /avatary/agent.log`
- Frontend logs: Browser console
- Configuration: `/var/www/avatar /avatary/.env`

## Quick Start

1. Start the agent (it will automatically use VisualAwareAgent)
2. Connect with camera enabled
3. Ask: "ماذا ترى؟" (What do you see?)
4. Avatar should describe what it sees!

## Monitoring

Check logs in real-time:
```bash
tail -f /var/www/avatar\ /avatary/agent.log | grep -E "👁️|✅|💉"
```

Expected output:
```
👁️  Visual analysis received: أرى شخصًا...
✅ Visual context stored (will inject before next LLM call)
💉 Injecting visual context (2.3s old)
```
