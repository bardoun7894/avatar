# Call Center Voice Response Issue - Analysis & Fix Guide

## Quick Summary

Your call center application has a critical bug preventing voice responses from being sent to customers:

**Symptom:** Microphone works (customer can talk) but agent gives no voice response (customer hears silence)

**Root Cause:** Line 105 in `call_center_agent.py` uses the wrong API method: `VoiceAssistantOptions.create()` instead of `VoiceAssistant.create()`

**Impact:** The entire TTS (Text-to-Speech) pipeline fails to initialize, preventing any voice output from reaching the customer

---

## Documents in This Directory

### 1. **VOICE_PIPELINE_SUMMARY.txt** (START HERE)
   - Executive summary of the issue
   - Component-by-component status
   - Priority-ordered fixes
   - Verification steps
   - **Read this first for a quick overview**

### 2. **QUICK_FIX_REFERENCE.md**
   - One-page reference guide
   - The specific bug and fix code
   - Secondary issues
   - Testing checklist
   - **Use this while implementing the fix**

### 3. **DETAILED_CODE_FIX.md**
   - Line-by-line code changes
   - Complete function examples
   - Configuration updates
   - Step-by-step implementation
   - Import statement corrections
   - **Reference this for detailed implementation**

### 4. **AUDIO_PIPELINE_ANALYSIS.md**
   - Complete technical analysis
   - Architecture and component breakdown
   - Detailed issue identification
   - Docker container information
   - Configuration analysis
   - **Read this for comprehensive understanding**

---

## The Core Issue (30-Second Version)

**File:** `/var/www/avatar/callCenter/call_center_agent.py`  
**Line:** 105  
**Problem:** Using non-existent method `VoiceAssistantOptions.create()`  
**Solution:** Change to `VoiceAssistant.create()`

```python
# WRONG:
assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)

# RIGHT:
from livekit.agents import VoiceAssistant
assistant = VoiceAssistant.create(ctx=ctx, options=opts, initial_ctx=initial_ctx)
```

---

## Audio Pipeline Status

```
Working ✓                          Broken ✗
├─ Customer Microphone             ├─ VoiceAssistant Init (Line 105)
├─ LiveKit Audio Capture           ├─ TTS Voice Config (Line 98)
├─ STT (Whisper)                   ├─ Error Handling (Line 109)
├─ LLM (GPT-4)                     └─ Audio Output
└─ TTS Configuration
```

The break in the chain: VoiceAssistant fails to initialize → TTS never runs → No audio output

---

## Files Needing Changes

| File | Lines | Priority | Status |
|------|-------|----------|--------|
| `call_center_agent.py` | 105 | CRITICAL | API usage error |
| `call_center_agent.py` | 98 | HIGH | Not language-aware |
| `call_center_agent.py` | 109 | HIGH | Missing error handling |
| `config.py` | N/A | MEDIUM | Add voice config |
| `.env` | N/A | LOW | Verify variables |

---

## How to Fix (Step-by-Step)

### Step 1: Update call_center_agent.py
- Fix Line 105: Change to `VoiceAssistant.create()`
- Fix Line 98: Make TTS voice language-aware
- Fix Line 109: Add error handling

See `DETAILED_CODE_FIX.md` for exact code

### Step 2: Update config.py
- Add voice/TTS configuration section

See `DETAILED_CODE_FIX.md` for configuration block

### Step 3: Restart Docker
```bash
docker restart avatar-backend
docker logs -f avatar-backend
```

### Step 4: Test
- Look for: "🎙️ Starting voice assistant..." in logs
- Place a test call
- Verify customer hears agent voice

---

## Verification Checklist

- [ ] Read VOICE_PIPELINE_SUMMARY.txt
- [ ] Review DETAILED_CODE_FIX.md
- [ ] Update call_center_agent.py Line 105
- [ ] Update call_center_agent.py Line 98
- [ ] Add error handling to Line 109
- [ ] Update config.py with voice configuration
- [ ] Restart agent container
- [ ] Check logs for "Starting voice assistant..."
- [ ] Test with a real call
- [ ] Verify customer hears agent voice

---

## Key Insight

This is **NOT** a missing API key, missing configuration, or broken hardware. It's a specific SDK API usage error:

- ✗ The code tries to call `VoiceAssistantOptions.create()` (method doesn't exist)
- ✓ Should call `VoiceAssistant.create()` (correct method)

This single line fix will enable the entire voice response pipeline.

---

## Architecture Overview

```
Customer Call (WebRTC via LiveKit)
    ↓
┌───────────────────────────────────┐
│     LiveKit Call Room             │
│  (Avatar-Backend Container)       │
├───────────────────────────────────┤
│ STT (Whisper) ✓ Working          │
│ LLM (GPT-4)  ✓ Working           │
│ TTS (OpenAI) ✗ BROKEN (Line 105) │
│ Output Audio ✗ FAILS             │
└───────────────────────────────────┘
    ↓ (No audio sent back)
Customer hears silence
```

---

## Document Sizes

- AUDIO_PIPELINE_ANALYSIS.md: 260 lines (comprehensive analysis)
- DETAILED_CODE_FIX.md: 352 lines (implementation guide)
- QUICK_FIX_REFERENCE.md: 114 lines (quick reference)
- VOICE_PIPELINE_SUMMARY.txt: 185 lines (executive summary)

**Total:** 911 lines of detailed documentation

---

## Next Steps

1. **Quick Understanding:** Read `VOICE_PIPELINE_SUMMARY.txt` (5 min)
2. **Implementation:** Reference `DETAILED_CODE_FIX.md` (15 min)
3. **Apply Fixes:** Update three code sections (10 min)
4. **Test:** Restart container and test call (5 min)

**Total Time to Fix:** ~35 minutes

---

## Questions?

- **What's broken?** → See `VOICE_PIPELINE_SUMMARY.txt`
- **How do I fix it?** → See `DETAILED_CODE_FIX.md`
- **Why is this happening?** → See `AUDIO_PIPELINE_ANALYSIS.md`
- **What's the quick fix?** → See `QUICK_FIX_REFERENCE.md`

---

## Support Information

- **Primary Issue:** `call_center_agent.py` Line 105
- **Secondary Issues:** Lines 98, 109
- **Configuration:** `config.py`
- **Running Containers:** `avatar-backend`, `avatar-callcenter`
- **API Keys:** All present in `.env` (OPENAI_API_KEY, LIVEKIT credentials, etc.)

---

Generated: 2025-11-11  
Status: Ready for Implementation  
Severity: CRITICAL - Voice pipeline offline  
Estimated Fix Time: 35 minutes
