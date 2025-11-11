#!/usr/bin/env python3
"""
Audio Handler for Call Center
Manages transcription and speech synthesis for calls
"""

import os
import io
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
import time

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")) if OPENAI_AVAILABLE else None

# Create audio directory
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True, mode=0o755)


class AudioHandler:
    """Handles audio transcription and synthesis"""

    @staticmethod
    async def transcribe_audio(audio_data: bytes, filename: str = "audio.webm") -> Dict:
        """
        Convert speech to text using OpenAI Whisper API

        Args:
            audio_data: Raw audio bytes
            filename: Original filename for format detection

        Returns:
            Dictionary with transcription results
        """
        if not OPENAI_AVAILABLE or not client:
            logger.warning("OpenAI not available, using mock transcription")
            return {
                "success": True,
                "text": "[Mock transcription] Customer speech would be transcribed here",
                "language": "en",
                "confidence": 0.0
            }

        try:
            # Use OpenAI Whisper API for transcription
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, io.BytesIO(audio_data), "audio/webm"),
                language=None  # Auto-detect language
            )

            return {
                "success": True,
                "text": transcript.text,
                "language": "auto",
                "confidence": 1.0
            }

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "language": "en"
            }

    @staticmethod
    async def synthesize_speech(
        text: str,
        voice: str = "nova",
        language: str = "en"
    ) -> Tuple[bytes, str]:
        """
        Synthesize text to speech using OpenAI TTS API

        Args:
            text: Text to synthesize
            voice: Voice name (nova, alloy, echo, fable, onyx, shimmer)
            language: Language code for voice selection

        Returns:
            Tuple of (audio_bytes, file_path)
        """
        if not OPENAI_AVAILABLE or not client:
            logger.warning("OpenAI not available, using mock synthesis")
            # Return empty MP3 bytes for mock
            return b"", ""

        try:
            # Select voice based on language
            voice_map = {
                "ar": "alloy",  # Arabic-friendly voice
                "en": "nova",   # English-friendly voice
                "default": "nova"
            }
            selected_voice = voice_map.get(language, voice)

            # Use OpenAI TTS API
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice=selected_voice,
                input=text,
                response_format="mp3"
            )

            # Save audio file
            timestamp = int(time.time() * 1000)
            filename = f"response-{timestamp}.mp3"
            file_path = AUDIO_DIR / filename

            with open(file_path, "wb") as f:
                f.write(speech_response.content)

            logger.info(f"Synthesized audio saved: {filename}")

            return speech_response.content, f"/audio/{filename}"

        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            return b"", ""

    @staticmethod
    def get_audio_file(filename: str) -> Optional[bytes]:
        """
        Retrieve stored audio file

        Args:
            filename: Audio filename

        Returns:
            Audio bytes or None if not found
        """
        file_path = AUDIO_DIR / filename

        if not file_path.exists():
            logger.warning(f"Audio file not found: {filename}")
            return None

        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read audio file: {str(e)}")
            return None

    @staticmethod
    def encode_audio_base64(audio_bytes: bytes) -> str:
        """
        Encode audio to base64 for embedding in response

        Args:
            audio_bytes: Raw audio bytes

        Returns:
            Base64-encoded string with data URI prefix
        """
        encoded = base64.b64encode(audio_bytes).decode()
        return f"data:audio/mpeg;base64,{encoded}"

    @staticmethod
    async def cleanup_old_audio(max_age_hours: int = 24):
        """
        Clean up old audio files

        Args:
            max_age_hours: Maximum age of files to keep
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for audio_file in AUDIO_DIR.glob("*.mp3"):
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    audio_file.unlink()
                    logger.info(f"Cleaned up old audio file: {audio_file.name}")

        except Exception as e:
            logger.error(f"Audio cleanup failed: {str(e)}")


# FastAPI endpoints
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import FileResponse


async def create_audio_endpoints(app):
    """
    Register audio endpoints with FastAPI app

    Args:
        app: FastAPI application instance
    """

    @app.post("/api/transcribe")
    async def transcribe_audio(audio_file: UploadFile = File(...)):
        """
        Convert speech audio to text

        Request:
            multipart/form-data with audio_file

        Response:
            {
                "success": true,
                "text": "transcribed text",
                "language": "en",
                "confidence": 0.95
            }
        """
        try:
            audio_data = await audio_file.read()

            if not audio_data:
                raise HTTPException(status_code=400, detail="Empty audio file")

            result = await AudioHandler.transcribe_audio(
                audio_data,
                audio_file.filename or "audio.webm"
            )

            if not result.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "Transcription failed")
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Transcription endpoint error: {str(e)}")
            raise HTTPException(status_code=500, detail="Transcription failed")

    @app.post("/api/synthesize")
    async def synthesize_audio(request_data: Dict):
        """
        Convert text to speech

        Request:
            {
                "text": "Text to synthesize",
                "language": "en",
                "voice": "nova"
            }

        Response:
            {
                "success": true,
                "audio_url": "/audio/response-123456.mp3",
                "audio_base64": "data:audio/mpeg;base64,..."
            }
        """
        try:
            text = request_data.get("text")
            language = request_data.get("language", "en")
            voice = request_data.get("voice", "nova")

            if not text or len(text.strip()) == 0:
                raise HTTPException(status_code=400, detail="Empty text")

            audio_bytes, audio_url = await AudioHandler.synthesize_speech(
                text,
                voice,
                language
            )

            if not audio_bytes:
                raise HTTPException(status_code=500, detail="Synthesis failed")

            return {
                "success": True,
                "audio_url": audio_url,
                "audio_base64": AudioHandler.encode_audio_base64(audio_bytes)
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Synthesis endpoint error: {str(e)}")
            raise HTTPException(status_code=500, detail="Synthesis failed")

    @app.get("/audio/{filename}")
    async def get_audio(filename: str):
        """
        Serve stored audio files

        Args:
            filename: Audio filename

        Returns:
            MP3 audio file
        """
        # Validate filename to prevent path traversal
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        audio_bytes = AudioHandler.get_audio_file(filename)

        if not audio_bytes:
            raise HTTPException(status_code=404, detail="Audio not found")

        return FileResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            filename=filename
        )

    logger.info("Audio endpoints registered successfully")


# Export
__all__ = ["AudioHandler", "create_audio_endpoints"]
