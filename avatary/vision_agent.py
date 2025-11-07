"""
Vision Processing Agent Module
Standalone module for analyzing user video and extracting visual context
"""

import asyncio
from typing import Callable, Optional
from livekit import rtc
from vision_processor import VisionProcessor
import logging
import time

logger = logging.getLogger(__name__)


class VisionAgent:
    """Manages video track monitoring and visual analysis"""

    def __init__(self):
        self.vision_processor = VisionProcessor()
        self.vision_task: Optional[asyncio.Task] = None
        self.latest_analysis: Optional[str] = None
        self.last_update: Optional[float] = None
        self.callback: Optional[Callable] = None

    async def start_monitoring(self, room: rtc.Room, callback: Callable[[str], None]):
        """Start monitoring for user video tracks and analyze them"""
        self.callback = callback

        print("👁️  Vision Agent: Starting video track monitoring...")
        print(f"    Room: {room.name}")
        print(f"    Local participant: {room.local_participant.identity}")

        # Monitor for remote participants with video
        attempt = 0
        while True:
            await asyncio.sleep(2)
            attempt += 1

            remote_participants = room.remote_participants

            if attempt % 5 == 0:
                print(f"👁️  Vision Agent: Checking participants ({len(remote_participants)} total)")
                for p in remote_participants.values():
                    print(f"      - {p.identity}: {len(p.track_publications)} tracks")

            for participant in remote_participants.values():
                # Skip agent itself
                if participant.identity == room.local_participant.identity:
                    continue

                print(f"👁️  Vision Agent: Scanning {participant.identity}...")

                for track_sid, pub in participant.track_publications.items():
                    if pub.source == rtc.TrackSource.SOURCE_CAMERA:
                        print(f"      ✅ Camera track found!")

                        await asyncio.sleep(1)  # Wait for subscription

                        if pub.track and not self.vision_task:
                            video_track = pub.track
                            print(f"📹 Vision Agent: Got video from {participant.identity}")
                            print("🎥 Vision Agent: Starting analysis loop...")

                            try:
                                self.vision_task = asyncio.create_task(
                                    self._analysis_loop(video_track)
                                )
                                print("✅ Vision Agent: Analysis task started!")
                                return  # Exit monitoring loop once we have video
                            except Exception as e:
                                print(f"❌ Vision Agent: Failed to start analysis: {e}")
                                import traceback
                                traceback.print_exc()

    async def _analysis_loop(self, video_track: rtc.RemoteVideoTrack):
        """Continuous analysis loop with callback"""
        async def handle_update(analysis: str):
            """Internal callback wrapper"""
            self.latest_analysis = analysis
            self.last_update = time.time()

            print(f"👁️  Vision Agent: Analysis complete ({len(analysis)} chars)")

            if self.callback:
                await self.callback(analysis)

        await self.vision_processor.start_continuous_analysis(
            video_track,
            callback=handle_update
        )

    def get_latest_context(self) -> Optional[dict]:
        """Get latest visual context with metadata"""
        if not self.latest_analysis:
            return None

        return {
            "analysis": self.latest_analysis,
            "timestamp": self.last_update,
            "age_seconds": time.time() - self.last_update if self.last_update else None,
            "is_fresh": (time.time() - self.last_update < 10) if self.last_update else False
        }

    async def stop(self):
        """Stop vision processing"""
        if self.vision_task:
            self.vision_task.cancel()
            try:
                await self.vision_task
            except asyncio.CancelledError:
                pass
            print("🛑 Vision Agent: Stopped")