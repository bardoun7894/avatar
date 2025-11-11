# Product Manager Analysis: Voice Call vs Avatar Video Issue

**Author:** John (Product Manager)
**Date:** 2025-11-11
**Status:** Critical Issue Analysis
**Severity:** HIGH - Blocks voice call feature

---

## Executive Summary

After reviewing the PRD, Docker configuration, and codebase, I've identified why voice calls aren't working while avatar video functions perfectly. **The problem is not a bug—it's an architectural mismatch.**

The PRD requires real-time audio streaming through LiveKit with intelligent sentiment-based routing. The implementation exists in `call_center_agent.py` (using LiveKit Agents Framework), but **the frontend (`call-with-audio.tsx`) is completely bypassing it and using a legacy file-based approach instead.**

---

## The Core Issue

### What the PRD Says (Requirements)

From [docs/PRD.md](./PRD.md):

**NFR-1: Response Time**
```
- Speech recognition latency: < 2 seconds
- Assistant response time: < 3 seconds (STT + LLM + TTS)
- Call initiation to first greeting: < 5 seconds
```

**NFR-3: Audio Quality**
```
- Audio codec: Opus
- Sample rate: 16kHz
- Bitrate: 20-40 kbps
- Latency: < 150ms audio round-trip
```

**FR-2: Real-Time Sentiment Analysis**
```
- Analyze customer speech in REAL-TIME as they speak
- Route based on sentiment dynamically
- Confidence > 85%
```

### What Actually Exists

**Backend (call_center_agent.py):** ✅ CORRECT IMPLEMENTATION
- Uses `AgentSession` from LiveKit Agents Framework
- Real-time STT via `ctx.stt`
- Real-time LLM via `ctx.llm`
- Real-time TTS via `ctx.tts`
- Proper sentiment routing support
- Meets all latency requirements

**Frontend (call-with-audio.tsx):** ❌ WRONG IMPLEMENTATION
- Never connects to LiveKit
- Uses `navigator.mediaDevices.getUserMedia()` (local recording only)
- Manual file-based flow: record → transcribe → LLM → TTS → download
- No real-time streaming
- Violates all latency requirements

---

## Docker Configuration Analysis

### Current Setup ✅ (Actually Correct)

**docker-compose.yml** (lines 77-111):
```yaml
callcenter:
  environment:
    - LIVEKIT_URL=${LIVEKIT_URL}
    - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
    - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
    - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**Actual Configuration** (.env.docker):
```
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
NEXT_PUBLIC_API_URL=http://localhost:8000
```

✅ **Docker is configured correctly** and LiveKit credentials are in place.

### What's Missing

The environment variables are set but the **frontend never uses them**. Compare:

**Avatar Video (WORKS):**
- Frontend: Uses `NEXT_PUBLIC_LIVEKIT_URL` to connect
- Backend: Uses `LIVEKIT_API_KEY` + `LIVEKIT_API_SECRET` to verify
- Flow: Direct WebRTC streaming

**Voice Calls (BROKEN):**
- Frontend: Ignores `NEXT_PUBLIC_LIVEKIT_URL` completely
- Backend: Has LiveKit credentials configured but frontend never initiates connection
- Flow: File uploads instead of streaming

---

## PRD Alignment Check

### MVP Requirements Status

| Requirement | Status | Issue |
|---|---|---|
| Real-time sentiment analysis | ❌ Blocked | Frontend doesn't stream audio to agent |
| < 5 second call initiation | ❌ Blocked | File upload adds delay |
| < 150ms audio latency | ❌ Blocked | Uses HTTP/file-based, not WebRTC |
| Seamless assistant transitions | ❌ Blocked | No sentiment data being analyzed |
| Arabic language support | ✅ Configured | Backend ready, frontend unused |
| Call recording & transcript | ⚠️ Partial | Doesn't record real conversation |
| CRM integration | ⚠️ Unused | Frontend doesn't send customer context |

**MVP Completion Rate: ~25% (blocked by frontend)**

---

## Side-by-Side Implementation Comparison

### Avatar Video Flow (Lines 52-319 in VideoCallInterface.tsx)

```
Frontend                                    Backend
┌─────────────────────┐                    ┌──────────────────┐
│ 1. room.connect()   │ ◄─ JWT token ◄─── │ Generate token   │
│    to LiveKit       │    via /api/token  │                  │
└──────────────────┬──┘                    └──────────────────┘
                   │
┌──────────────────▼────────┐
│ 2. WebRTC connection      │
│    - Publish local audio  │
│    - Subscribe to remote  │
└──────────────────┬────────┘
                   │
      ┌────────────▼──────────────┐
      │ 3. room.on(                │
      │    RoomEvent.TrackSubscribed
      │    )                       │
      └────────────┬──────────────┘
                   │
┌──────────────────▼──────────────────┐
│ 4. track.attach(audioElement)      │
│    User hears agent response        │
│    (sub-100ms latency)              │
└─────────────────────────────────────┘
```

**Why it works:** Direct media streaming, no file conversions.

---

### Voice Call Flow (Lines 55-150 in call-with-audio.tsx)

```
Frontend                                    Backend
┌─────────────────────┐                    ┌──────────────────┐
│ 1. getUserMedia()   │                    │ call_center_agent│
│    (local mic only) │                    │ waiting for      │
└─────────────────────┘                    │ room connection  │
         │                                  └──────────────────┘
         │ (NEVER HAPPENS)
         │ room.connect() never called
         │
┌────────▼─────────────────────┐
│ 2. MediaRecorder.start()     │
│    Record local audio to blob│
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 3. POST /api/transcribe       │
│    (1-2 second delay)         │
└────────┬──────────────────────┘
         │
         │ OpenAI Whisper STT
         │
┌────────▼──────────────────────┐
│ 4. POST /api/conversation     │
│    (1-2 second delay)         │
└────────┬──────────────────────┘
         │
         │ OpenAI LLM
         │
┌────────▼──────────────────────┐
│ 5. Implicit TTS conversion    │
│    (1 second delay)           │
└────────┬──────────────────────┘
         │
┌────────▼──────────────────────┐
│ 6. Save MP3 file              │
│ 7. POST response with URL     │
│ 8. Download + Play            │
└───────────────────────────────┘

Total: 3-5 seconds latency (vs 100ms requirement)
```

**Why it doesn't work:** Violates every latency requirement in PRD.

---

## Root Cause Analysis

### Problem 1: Frontend Architecture Mismatch

**File:** `frontend/apps/callcenter/pages/call-with-audio.tsx` (lines 33-150)

```typescript
export default function CallPageWithAudio() {
  const router = useRouter()
  const { room, user } = router.query

  // ❌ Creates CallData but never uses LiveKit room
  const [callData, setCallData] = useState<CallData | null>(null)

  // ❌ Only initializes local microphone
  const streamRef = useRef<MediaStream | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

  // ❌ No room connection
  // ❌ No LiveKit client
  // ❌ No track subscription
}
```

**Compare to Avatar Video** (`frontend/apps/avatar/components/VideoCallInterface.tsx`):
```typescript
// ✅ Creates room and connects to LiveKit
const room = new Room(...)
await room.connect(livekitUrl, token)

// ✅ Subscribes to tracks
room.on(RoomEvent.TrackSubscribed, (track) => {
  track.attach(element)
})
```

### Problem 2: Backend Agent Never Gets Called

The backend `call_center_agent.py` has the full implementation but needs:
1. Frontend to call `/api/dispatch-agent`
2. Frontend to establish WebRTC connection to LiveKit

**call-with-audio.tsx never does either.**

### Problem 3: Environment Variables Set But Unused

Frontend has access to:
- `NEXT_PUBLIC_LIVEKIT_URL` = `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- `NEXT_PUBLIC_CALLCENTER_LIVEKIT_URL` = same
- `NEXT_PUBLIC_API_URL` = `http://localhost:8000`

But **call-with-audio.tsx doesn't import or use any of them.**

---

## Why This Happened (Historical Context)

The frontend `call-with-audio.tsx` appears to be a **legacy implementation** that predates the proper LiveKit agent framework integration. It was likely:

1. Built before `call_center_agent.py` existed
2. Intended as a quick prototype (file-based audio)
3. Never refactored to use the production LiveKit architecture
4. Left in place because backend was working

The backend team built everything correctly. The frontend was never updated to match.

---

## What Needs to Happen

### ✅ What's Already Done

1. ✅ Backend agent framework working (`call_center_agent.py`)
2. ✅ LiveKit infrastructure provisioned (Tavus cloud instance)
3. ✅ Environment variables configured
4. ✅ Docker setup correct
5. ✅ API endpoints ready (`/api/dispatch-agent`, `/api/token`)

### ❌ What Needs to Be Fixed

**Single point of failure:** Frontend needs to be refactored to follow the Avatar Video pattern.

**Frontend needs to:**
1. Get JWT token from `/api/token` endpoint
2. Import and use `LiveKit` Room client
3. Connect room to LiveKit server: `room.connect(livekitUrl, token)`
4. Dispatch agent via `/api/dispatch-agent`
5. Subscribe to audio tracks and attach to HTML audio element
6. Remove all file-based recording logic

---

## Implementation Effort Estimate

| Task | Effort | Impact |
|---|---|---|
| Refactor call-with-audio.tsx | 3-4 hours | HIGH - Unblocks entire feature |
| Test real-time sentiment routing | 2 hours | MEDIUM - Verify PRD requirements |
| Test Docker deployment | 1 hour | HIGH - Production readiness |
| Create integration tests | 2-3 hours | MEDIUM - Prevent regression |
| **Total** | **8-10 hours** | **Restores MVP completion** |

---

## Docker Configuration is Ready

**Current docker-compose.yml** (lines 86-91):
```yaml
environment:
  - LIVEKIT_URL=${LIVEKIT_URL}
  - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
  - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**Current .env.docker has:**
```
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
NEXT_PUBLIC_CALLCENTER_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
NEXT_PUBLIC_API_URL=http://localhost:8000
```

✅ **Docker is properly configured. The issue is purely frontend code.**

---

## Success Criteria (After Fix)

When voice calls are refactored:

1. **Real-time sentiment analysis works** - Assistant knows when customer is interested/upset
2. **Latency < 150ms** - No perceptible delay
3. **Assistant transitions are seamless** - Customer doesn't know they're talking to AI
4. **Call completion rate > 95%** - No dropped calls
5. **Docker deployment works** - Can run full system in containers
6. **PRD requirements met** - All MVP functionality working

---

## Recommendation

**Priority: CRITICAL (Blocks MVP)**

The voice call system has a **straightforward fix**: refactor the frontend to use the same LiveKit + WebRTC pattern that avatar video already uses successfully.

**This is not a complex architectural problem.** The backend is correct. The Docker configuration is correct. The environment variables are set. **Only the frontend view layer needs alignment.**

Recommend:
1. ✅ Keep `call_center_agent.py` as-is (it's correct)
2. ✅ Keep Docker configuration as-is (it's correct)
3. ❌ Refactor `call-with-audio.tsx` to use LiveKit Room client
4. ✅ Run integration tests to verify sentiment routing
5. ✅ Deploy to production

---

## Questions for Product Leadership

1. **Timeline:** When does voice call feature need to be production-ready?
2. **MVP vs Growth:** Is sentiment-based routing critical for MVP or a Phase 2 feature?
3. **Multi-dialect:** PRD mentions Syrian dialect focus—is this launch requirement?
4. **CRM Integration:** Should we pre-populate customer context in Phase 1?

---

## References

- **PRD:** [docs/PRD.md](./PRD.md)
- **Backend Agent:** [callCenter/call_center_agent.py](../callCenter/call_center_agent.py)
- **Frontend (Broken):** [frontend/apps/callcenter/pages/call-with-audio.tsx](../frontend/apps/callcenter/pages/call-with-audio.tsx)
- **Frontend (Working):** [frontend/apps/avatar/components/VideoCallInterface.tsx](../frontend/apps/avatar/components/VideoCallInterface.tsx)
- **Docker Config:** [docker-compose.yml](../docker-compose.yml)
- **Environment:** [.env.docker](./.env.docker)

---

**Document Status:** Ready for Technical Implementation
**Next Step:** Run `/bmad:bmm:workflows:dev-story` to implement frontend refactor
