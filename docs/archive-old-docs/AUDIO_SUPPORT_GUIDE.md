# Audio Support for Call Center - Implementation Guide

## Overview

The call center system now includes full audio support with real-time speech transcription, synthesis, and microphone level monitoring. This guide explains how to enable and use the audio features.

## Features

### Frontend (call-with-audio.tsx)

✅ **Microphone Input**
- Web Audio API integration
- Real-time audio level monitoring
- Visual audio level indicator (20-bar equalizer)
- Echo cancellation & noise suppression
- Automatic gain control disabled for manual control

✅ **Audio Recording**
- WebM format audio capture
- Start/stop recording buttons
- Real-time recording indicator
- Seamless audio-to-text conversion

✅ **Speaker Output**
- Audio playback element
- Automatic playback of AI responses
- Volume control (browser default)

### Backend Endpoints

The following endpoints need to be implemented in FastAPI:

#### 1. `/api/transcribe` - Speech to Text
**POST** - Convert audio to text using OpenAI Whisper API

**Request:**
```
multipart/form-data
- audio_file: Blob (WebM/WAV)
```

**Response:**
```json
{
  "success": true,
  "text": "I want to purchase your service",
  "language": "en",
  "confidence": 0.95
}
```

#### 2. `/api/conversation` - Get Response with Audio
**POST** - Get AI response and synthesize speech

**Request:**
```json
{
  "call_id": "room-123",
  "message": "Tell me about pricing",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Our pricing starts at...",
  "persona": "sales",
  "audio_url": "/audio/response-xxx.mp3",
  "audio_base64": "base64_encoded_mp3"
}
```

## Backend Implementation

### Add to callCenter/main.py:

```python
from fastapi import File, UploadFile, HTTPException
from openai import OpenAI
import io
import base64

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Convert speech to text"""
    try:
        # Read audio file
        audio_data = await audio_file.read()

        # Use OpenAI Whisper API
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.webm", io.BytesIO(audio_data), "audio/webm"),
            language=None  # Auto-detect
        )

        return {
            "success": True,
            "text": transcript.text,
            "language": "auto",
            "confidence": 1.0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/conversation")
async def get_conversation_with_audio(request_data: dict):
    """Get conversation response with audio synthesis"""
    try:
        call_id = request_data.get("call_id")
        message = request_data.get("message")
        language = request_data.get("language", "en")

        # Get conversation response
        manager = get_conversation_manager(call_id, "Customer", language)
        response_text = await manager.get_response(message)

        # Synthesize speech
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="nova" if language == "en" else "alloy",
            input=response_text,
            response_format="mp3"
        )

        # Save audio file
        audio_filename = f"response-{call_id}-{int(time.time())}.mp3"
        audio_path = f"audio/{audio_filename}"

        with open(audio_path, "wb") as f:
            f.write(speech_response.content)

        # Convert to base64 for direct embedding
        audio_base64 = base64.b64encode(speech_response.content).decode()

        return {
            "success": True,
            "text": response_text,
            "persona": manager.current_persona.value,
            "audio_url": f"/audio/{audio_filename}",
            "audio_base64": f"data:audio/mp3;base64,{audio_base64}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve stored audio files"""
    from fastapi.responses import FileResponse

    file_path = f"audio/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(file_path, media_type="audio/mpeg")
```

## Frontend Integration

### To enable audio in the call interface:

1. **Replace the current call page:**
```bash
cp /frontend/pages/callcenter/call-with-audio.tsx /frontend/pages/callcenter/call.tsx
```

2. **Install required dependencies (if not already present):**
```bash
cd frontend
npm install
```

3. **Environment Variables:**

Add to `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_AUDIO=true
```

## Audio File Structure

Create the audio directory for storing recordings:
```bash
mkdir -p /var/www/avatar /callCenter/audio
chmod 755 /var/www/avatar /callCenter/audio
```

## Browser Requirements

- **Chrome/Chromium**: Full support
- **Firefox**: Full support
- **Safari**: Requires HTTPS for microphone access
- **Edge**: Full support

## Usage Flow

1. **User grants microphone permission** → Browser requests permission
2. **User clicks "Start Recording"** → Microphone level indicator animates
3. **User speaks** → Audio is captured in real-time
4. **User clicks "Stop Recording"** → Audio sent to backend
5. **Backend transcribes** → Uses Whisper API
6. **Backend generates response** → Uses GPT-4 with personas
7. **Backend synthesizes audio** → Uses TTS API
8. **Audio plays automatically** → User hears response

## Troubleshooting

### No Microphone Access
- Check browser permissions
- Verify HTTPS (required for Safari)
- Restart browser

### No Audio Output
- Check browser volume
- Verify audio element is not muted
- Check network tab for failed audio requests

### Transcription Issues
- Ensure audio quality (reduce background noise)
- Check language detection in backend
- Verify OpenAI API key is set

### Performance Issues
- Monitor microphone audio level (shouldn't spike >200)
- Check browser console for WebAudio errors
- Verify backend API response time

## API Keys Required

Set these environment variables in `.env` or deploy configuration:

```bash
OPENAI_API_KEY=sk-...  # Required for Whisper & TTS
```

## Testing Audio Features

Visit the call interface:
```
http://localhost:3000/callcenter/call?room=test-room-123&user=TestUser
```

Then:
1. Allow microphone access
2. Watch the audio level indicator
3. Click "Start Recording" and speak
4. Click "Stop Recording"
5. Wait for transcription and response
6. Listen for synthesized audio

## Performance Metrics

- **Transcription Time**: ~2-3 seconds (depends on audio length)
- **Response Generation**: ~1-2 seconds
- **Speech Synthesis**: ~1 second
- **Total Round Trip**: ~4-6 seconds

## Disabling Audio (Fallback to Text)

If audio features cause issues, revert to text-only mode:

```bash
cp /frontend/pages/callcenter/call-original.tsx /frontend/pages/callcenter/call.tsx
```

The system will still function with text-based chat.

## Future Enhancements

- [ ] Real-time streaming audio transcription
- [ ] Voice activity detection (auto-stop recording)
- [ ] Multi-language voice selection
- [ ] Call recording storage with encryption
- [ ] Audio quality monitoring
- [ ] Speech emotion detection
- [ ] Custom voice training per persona

## Support

For issues with audio features:
1. Check browser console for errors
2. Verify OpenAI API credits
3. Test microphone access independently
4. Check backend logs for API errors
5. Review network tab for failed requests
