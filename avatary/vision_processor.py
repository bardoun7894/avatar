"""
Vision Processor for AI Agent
Captures and analyzes video frames from user's camera using GPT-4 Vision
"""

import asyncio
import base64
import io
import os
from typing import Optional
from PIL import Image
import numpy as np
from openai import AsyncOpenAI
from livekit import rtc
import logging

logger = logging.getLogger(__name__)

class VisionProcessor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.last_analysis = None
        self.last_frame_time = 0
        self.analysis_interval = 0.8  # Analyze every 0.8 seconds (much faster for face recognition)
        self.is_running = False

    async def capture_frame_from_track(self, video_track: rtc.RemoteVideoTrack) -> Optional[bytes]:
        """Capture a single frame from video track"""
        stream = None
        try:
            # Create video stream and get one frame
            stream = rtc.VideoStream(video_track)

            async for event in stream:
                frame = event.frame

                # Convert frame to RGBA buffer using correct API
                argb_frame = frame.convert(rtc.VideoBufferType.RGBA)

                # Create PIL Image from buffer
                img = Image.frombytes(
                    "RGBA",
                    (frame.width, frame.height),
                    argb_frame.data
                )

                # Convert to RGB and encode as JPEG
                rgb_img = img.convert("RGB")
                buffered = io.BytesIO()
                rgb_img.save(buffered, format="JPEG", quality=60)  # Lower quality to save memory

                jpeg_bytes = buffered.getvalue()

                # Clean up
                buffered.close()
                del img, rgb_img, argb_frame

                # Return after getting first frame
                return jpeg_bytes

        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            return None
        finally:
            # Always close stream to prevent memory leak
            if stream:
                try:
                    await stream.aclose()
                except:
                    pass

    async def analyze_image(self, image_bytes: bytes, context: str = "") -> Optional[str]:
        """Analyze image using GPT-4 Vision"""
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Ultra-simplified prompt for faster processing - Just detect person
            prompt = """Describe the main person in center of frame in 1 sentence. Arabic only."""

            if context:
                prompt += f"\n\nAdditional context: {context}"

            # Call GPT-4 Vision API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Faster, cheaper mini model - still accurate for vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"  # Use "low" for faster processing
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50  # Very short response - just need basic description for context
            )

            analysis = response.choices[0].message.content
            self.last_analysis = analysis

            logger.info(f"Vision analysis: {analysis[:100]}...")
            return analysis

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return None

    async def start_continuous_analysis(
        self,
        video_track: rtc.RemoteVideoTrack,
        callback=None
    ):
        """Continuously capture and analyze frames"""
        self.is_running = True
        logger.info("🎥 Starting continuous vision analysis...")

        try:
            while self.is_running:
                # Capture frame
                frame_bytes = await self.capture_frame_from_track(video_track)

                if frame_bytes:
                    # Analyze frame
                    analysis = await self.analyze_image(frame_bytes)

                    if analysis and callback:
                        # Pass both analysis and frame_bytes for face recognition
                        await callback(analysis, frame_bytes)

                # Wait before next capture
                await asyncio.sleep(self.analysis_interval)

        except Exception as e:
            logger.error(f"Vision processing error: {e}")
        finally:
            self.is_running = False

    def stop(self):
        """Stop continuous analysis"""
        self.is_running = False
        logger.info("🛑 Stopping vision analysis")

    def get_last_analysis(self) -> Optional[str]:
        """Get the most recent vision analysis"""
        return self.last_analysis
