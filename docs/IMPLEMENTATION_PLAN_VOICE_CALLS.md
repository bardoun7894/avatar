# Implementation Plan: Fix Voice Call Frontend

**Product Manager:** John
**Created:** 2025-11-11
**Type:** Technical Specification for Frontend Refactor
**Priority:** CRITICAL - Unblocks MVP

---

## Overview

This document provides a detailed, step-by-step plan to refactor the voice call frontend (`call-with-audio.tsx`) to use real-time WebRTC streaming through LiveKit, matching the successful avatar video implementation.

**Scope:** Refactor single file to use LiveKit Room client pattern
**Effort:** 8-10 hours (1 developer)
**Risk:** LOW (Avatar video proves this pattern works)

---

## Current vs Target Architecture

### Current (Broken)

```
┌─────────────────────────────────┐
│ call-with-audio.tsx             │
├─────────────────────────────────┤
│ ✗ navigator.getUserMedia()      │
│ ✗ MediaRecorder local recording │
│ ✗ POST /api/transcribe          │
│ ✗ POST /api/conversation        │
│ ✗ Manual TTS + file download    │
│ ✗ 3-5 second latency            │
│ ✗ NO LiveKit connection         │
│ ✗ NO sentiment analysis         │
└─────────────────────────────────┘
                  ↓
Result: 25% MVP completion, doesn't meet requirements
```

### Target (Using Avatar Video Pattern)

```
┌──────────────────────────────────┐
│ call-with-audio.tsx (refactored) │
├──────────────────────────────────┤
│ ✓ GET /api/token (JWT)           │
│ ✓ new Room() + connect()         │
│ ✓ WebRTC media streaming         │
│ ✓ Track subscription + attach    │
│ ✓ POST /api/dispatch-agent       │
│ ✓ Real-time STT/LLM/TTS          │
│ ✓ < 150ms latency                │
│ ✓ Sentiment analysis working     │
│ ✓ CRM context injection          │
└──────────────────────────────────┘
              ↓
Result: 100% MVP completion, meets all requirements
```

---

## Detailed Implementation Steps

### Step 1: Import LiveKit Libraries (30 min)

**File:** `frontend/apps/callcenter/pages/call-with-audio.tsx`

**Current imports:**
```typescript
import Head from 'next/head'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import ControlBar from '../components/ControlBar'
import ChatPanel from '../components/ChatPanel'
```

**Add these imports:**
```typescript
// LiveKit imports
import {
  LiveKitRoom,
  VideoConference,
  useRoom,
  useToken,
} from '@livekit/react'
import { Room, RoomEvent, ParticipantEvent } from 'livekit-client'
```

**Why:** These provide the WebRTC connection management and event handling needed for real-time streaming.

---

### Step 2: Remove Legacy Audio Initialization (1 hour)

**What to remove:**
- Lines 47-51: `mediaRecorderRef`, `audioContextRef`, `analyserRef`, etc.
- Lines 89-124: `initializeAudio()` function (not needed with LiveKit)
- Lines 126-136: `monitorAudioLevel()` function
- Lines 138-150: `startRecording()` function
- All file-based MediaRecorder code

**What to keep:**
- `useState` hooks for messages, UI state
- `useRouter` for room/user params
- `audioElementRef` (but will be used differently)

**Code to delete:**
```typescript
// DELETE: Not needed with WebRTC
const mediaRecorderRef = useRef<MediaRecorder | null>(null)
const audioContextRef = useRef<AudioContext | null>(null)
const analyserRef = useRef<AnalyserNode | null>(null)
const audioChunksRef = useRef<Blob[]>([])
const streamRef = useRef<MediaStream | null>(null)

// DELETE: These functions rely on old pattern
const initializeAudio = async () => { ... }
const monitorAudioLevel = () => { ... }
const startRecording = async () => { ... }
```

---

### Step 3: Add LiveKit Token Fetching (30 min)

**Add new function:**
```typescript
// Fetch JWT token from backend
const getToken = async (roomName: string, userName: string): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/api/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      room: roomName,
      identity: userName,
      metadata: {
        userName: userName,
        role: 'customer',
      }
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to get token: ${response.statusText}`)
  }

  const data = await response.json()
  return data.token
}
```

**Why:** LiveKit requires JWT tokens to authenticate connections. This mimics the avatar video pattern.

---

### Step 4: Add Agent Dispatch (30 min)

**Add new function:**
```typescript
const dispatchAgent = async (roomName: string) => {
  console.log(`📞 Dispatching agent to room: ${roomName}`)

  try {
    const response = await fetch(`${API_BASE_URL}/api/dispatch-agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room: roomName,
        assistant_type: 'reception', // Can be 'reception', 'sales', 'support'
      }),
    })

    if (!response.ok) {
      throw new Error(`Failed to dispatch agent: ${response.statusText}`)
    }

    console.log(`✅ Agent dispatched to room: ${roomName}`)
  } catch (error) {
    console.error('❌ Agent dispatch failed:', error)
    throw error
  }
}
```

**Why:** This tells the backend to start the agent in the LiveKit room. Without this, the agent never joins.

---

### Step 5: Update useEffect Hook for Room Connection (1.5 hours)

**Replace the current useEffect (lines 55-87) with:**

```typescript
useEffect(() => {
  if (!room || !user) {
    console.log('⏳ Waiting for room and user parameters...')
    return
  }

  console.log('🎙️ Initializing voice call...')
  console.log(`📍 Room: ${room}`)
  console.log(`👤 User: ${user}`)

  const initializeCall = async () => {
    try {
      // Step 1: Get LiveKit token
      console.log('🔐 Fetching LiveKit token...')
      const token = await getToken(room as string, user as string)
      console.log('✅ Token received')

      // Step 2: Dispatch agent to room
      console.log('📲 Dispatching agent...')
      await dispatchAgent(room as string)
      console.log('✅ Agent dispatched')

      // Step 3: Initialize call data
      const newCall: CallData = {
        callId: room as string,
        status: 'in_progress',
        duration: 0,
      }
      setCallData(newCall)
      setCallStartTime(new Date())
      console.log('✅ Call initialized')

      // Step 4: Add welcome message
      const welcomeMsg: Message = {
        id: `msg-${Date.now()}`,
        role: 'bot',
        content: 'أهلاً وسهلاً بكم في خدمة الاستقبال الآلية. Welcome to our automated reception service.',
        timestamp: new Date(),
        userName: 'IVR Bot',
      }
      setMessages([welcomeMsg])
      console.log('✅ Welcome message added')

      // Note: WebRTC connection will be established by LiveKitRoom component
      console.log('✅ Initialization complete')
    } catch (error) {
      console.error('❌ Call initialization failed:', error)
      // Add error message to chat
      setMessages(prev => [...prev, {
        id: `msg-${Date.now()}`,
        role: 'system',
        content: `Call initialization failed: ${error}`,
        timestamp: new Date(),
      }])
    }
  }

  initializeCall()
}, [room, user])
```

---

### Step 6: Add LiveKit Event Handlers (2 hours)

**Add new useEffect hook for LiveKit room events:**

```typescript
// Handle remote audio track attachment
useEffect(() => {
  if (!room) return

  const handleTrackSubscribed = (track: any) => {
    console.log(`🎵 Track subscribed: ${track.kind}`)

    if (track.kind === 'audio') {
      // Attach agent's audio to the audio element
      if (audioElementRef.current) {
        track.attach(audioElementRef.current)
        console.log('✅ Agent audio attached to speaker')
      }
    }
  }

  const handleTrackUnsubscribed = (track: any) => {
    console.log(`❌ Track unsubscribed: ${track.kind}`)
    // Clean up
    if (track.kind === 'audio' && audioElementRef.current) {
      track.detach(audioElementRef.current)
    }
  }

  const handleRoomDisconnect = () => {
    console.log('📞 Room disconnected')
    setCallData(prev => prev ? { ...prev, status: 'completed' } : null)
  }

  // Subscribe to room events
  if (room instanceof Room) {
    room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed)
    room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed)
    room.on(RoomEvent.Disconnected, handleRoomDisconnect)

    return () => {
      room.off(RoomEvent.TrackSubscribed, handleTrackSubscribed)
      room.off(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed)
      room.off(RoomEvent.Disconnected, handleRoomDisconnect)
    }
  }
}, [room])
```

---

### Step 7: Update JSX Render Structure (1.5 hours)

**Replace the component JSX with:**

```typescript
return (
  <>
    <Head>
      <title>Call Center - Audio Call</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </Head>

    <div style={{ display: 'flex', height: '100vh', flexDirection: 'column' }}>
      {/* Hidden audio element for agent output */}
      <audio
        ref={audioElementRef}
        autoPlay
        controls={false}
        style={{ display: 'none' }}
      />

      {/* Call Header */}
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h1>Call Center</h1>
        {callData && (
          <div>
            <p>Call ID: {callData.callId}</p>
            <p>Status: {callData.status}</p>
            <p>Duration: {callData.duration}s</p>
          </div>
        )}
      </div>

      {/* Main Call Interface */}
      <div style={{ display: 'flex', flex: 1, gap: '20px', padding: '20px' }}>
        {/* Chat/Conversation Panel */}
        <div style={{ flex: 1, overflowY: 'auto', border: '1px solid #ddd', padding: '20px' }}>
          <h2>Conversation</h2>
          {messages.map((msg) => (
            <div key={msg.id} style={{ marginBottom: '10px', padding: '10px', backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5', borderRadius: '5px' }}>
              <strong>{msg.userName || msg.role}:</strong> {msg.content}
              <small style={{ display: 'block', marginTop: '5px', color: '#999' }}>
                {msg.timestamp.toLocaleTimeString()}
              </small>
            </div>
          ))}
        </div>

        {/* Control Panel */}
        <div style={{ width: '300px', borderLeft: '1px solid #ddd', paddingLeft: '20px' }}>
          <h3>Controls</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              onClick={() => setIsMuted(!isMuted)}
              style={{ padding: '10px', backgroundColor: isMuted ? '#f44336' : '#4caf50', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
            >
              {isMuted ? 'Unmute' : 'Mute'}
            </button>
            <button
              onClick={() => setIsChatOpen(!isChatOpen)}
              style={{ padding: '10px', backgroundColor: '#2196f3', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
            >
              {isChatOpen ? 'Close Chat' : 'Open Chat'}
            </button>
            <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#fff3e0', borderRadius: '5px' }}>
              <p style={{ margin: '0 0 10px 0' }}>Audio Level: {audioLevel}</p>
              <div style={{ height: '20px', backgroundColor: '#ddd', borderRadius: '3px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    backgroundColor: '#4caf50',
                    width: `${Math.min(audioLevel * 1.5, 100)}%`,
                    transition: 'width 0.1s'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </>
)
```

---

### Step 8: Remove Audio Level Monitoring (Dependencies Update)

Since LiveKit handles all real-time audio, remove the `monitorAudioLevel()` call from initialization.

**Delete:**
```typescript
// No longer needed
monitorAudioLevel()
```

If you want to keep audio level monitoring (nice-to-have), you'll need to add an analyser node to the remote audio track, but this is not required for functionality.

---

## Testing Checklist

### Unit Tests
```
✓ getToken() returns valid JWT
✓ dispatchAgent() successfully calls backend
✓ Conversation state updates correctly
✓ Messages display in correct order
✓ Call status transitions work
```

### Integration Tests
```
✓ Full call flow: token → connect → dispatch → audio stream
✓ Agent audio plays through speaker
✓ Mute button works (pauses local audio)
✓ Chat messages update in real-time
✓ Call termination cleans up resources
✓ Error handling (network failures, timeouts)
```

### End-to-End Tests
```
✓ Docker deployment: frontend + callcenter + redis running
✓ Call from browser connects to LiveKit
✓ Agent joins room and responds
✓ Sentiment analysis routing works
✓ Multi-turn conversations work
✓ Call recording stored correctly
✓ Latency < 150ms measured
```

---

## Configuration Requirements

### Frontend Environment Variables Needed

These should already be set in `.env.docker`:

```
NEXT_PUBLIC_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CALLCENTER_LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
```

### Backend Endpoints Required

These endpoints must be available:

```
GET /api/token
  Input: { room: string, identity: string, metadata?: object }
  Output: { token: string }

POST /api/dispatch-agent
  Input: { room: string, assistant_type: 'reception'|'sales'|'support' }
  Output: { status: 'dispatched' }

POST /api/health
  Output: { status: 'ok' }
```

---

## Rollback Plan

If something goes wrong:

1. **Git rollback:** `git checkout -- frontend/apps/callcenter/pages/call-with-audio.tsx`
2. **Revert changes:** `git revert <commit-hash>`
3. **Quick fix:** Keep the old `call-with-audio.tsx` in git history until new version is proven

---

## Known Issues & Mitigations

| Issue | Impact | Mitigation |
|---|---|---|
| Network latency spikes | Audio dropout | Implement jitter buffer in LiveKit config |
| Agent joins but audio doesn't play | Silent call | Check browser autoplay permissions |
| Token expires mid-call | Call drops | Implement token refresh logic before expiry |
| Multiple agents in room | Confusion | Add participant filtering to agent dispatch |

---

## Success Criteria

✅ All acceptance criteria from PRD met:
- [ ] Real-time sentiment analysis triggers routing
- [ ] Speech recognition latency < 2 seconds
- [ ] Assistant response time < 3 seconds
- [ ] Audio round-trip latency < 150ms
- [ ] Seamless assistant transitions (< 2 seconds)
- [ ] Call recording + transcript working
- [ ] CRM context injected into prompt
- [ ] Docker deployment successful
- [ ] Integration tests passing (100%)
- [ ] Manual end-to-end call successful

---

## Approval Checklist

Before deployment to production:

- [ ] Code review completed
- [ ] All tests passing (unit + integration + E2E)
- [ ] Docker image builds successfully
- [ ] Load testing done (100+ concurrent calls)
- [ ] Security audit passed (no XSS, injection, etc.)
- [ ] Performance profiling done (latency < 150ms)
- [ ] Documentation updated
- [ ] Staging deployment successful
- [ ] Customer UAT passed

---

## Timeline

**Estimated Effort Breakdown:**

| Phase | Duration | Details |
|---|---|---|
| Code Changes | 3-4 hours | Steps 1-7 above |
| Local Testing | 2 hours | Run through testing checklist |
| Integration Testing | 1-2 hours | Full end-to-end flow |
| Docker Testing | 1 hour | Build and run containers |
| Review + Refinement | 1 hour | Address feedback |
| **Total** | **8-10 hours** | 1 developer, 1-2 sprints |

---

## Next Steps

1. ✅ Assign developer to implement refactor (priority: P0)
2. ✅ Set up code review process (require PM + tech lead review)
3. ✅ Create GitHub issue with this plan
4. ✅ Deploy to staging after passing tests
5. ✅ Run customer UAT on staging
6. ✅ Deploy to production after UAT approval

---

## Questions?

- **Technical details:** See code comments in each step
- **Architecture:** Reference [PM_ANALYSIS_VOICE_CALL_ISSUE.md](./PM_ANALYSIS_VOICE_CALL_ISSUE.md)
- **Requirements:** See [PRD.md](./PRD.md)
- **Backend implementation:** See [callCenter/call_center_agent.py](../callCenter/call_center_agent.py)

---

**Document Approval:**
- [ ] Product Manager (John) - Ready
- [ ] Tech Lead
- [ ] DevOps Lead

**Status:** Ready for Implementation
**Created:** 2025-11-11
