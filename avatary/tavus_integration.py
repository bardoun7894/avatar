"""
Tavus Video Avatar Integration Module
Handles Tavus replica video avatar connection and management
"""

import os
import asyncio
from typing import Optional
from livekit import rtc
import logging

logger = logging.getLogger(__name__)


class TavusAvatarSession:
    """Manages Tavus video avatar session"""

    def __init__(self):
        self.tavus_api_key = os.getenv("TAVUS_API_KEY")
        self.tavus_persona_id = os.getenv("TAVUS_PERSONA_ID")
        self.tavus_replica_id = os.getenv("TAVUS_REPLICA_ID")
        self.livekit_url = os.getenv("LIVEKIT_URL")

        if not all([self.tavus_api_key, self.tavus_persona_id, self.tavus_replica_id]):
            raise ValueError("Missing Tavus credentials in environment variables")

    async def start(self, session, room: rtc.Room):
        """Start Tavus avatar in the LiveKit room"""
        import httpx

        print("🎬 Starting Tavus avatar...")
        print(f"   Replica ID: {self.tavus_replica_id}")
        print(f"   Persona ID: {self.tavus_persona_id}")

        # Create Tavus conversation
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://tavusapi.com/v2/conversations",
                headers={
                    "x-api-key": self.tavus_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "replica_id": self.tavus_replica_id,
                    "persona_id": self.tavus_persona_id,
                    "conversational_context": "أنت موظف استقبال في شركة أورنينا",
                    "custom_greeting": None,
                    "properties": {
                        "max_call_duration": 3600,
                        "participant_left_timeout": 60,
                        "enable_recording": False,
                        "enable_transcription": False,
                        "apply_greenscreen": False,
                        "language": "ar"
                    }
                }
            )

            if response.status_code != 201:
                raise Exception(f"Failed to create Tavus conversation: {response.text}")

            data = response.json()
            conversation_id = data.get("conversation_id")
            conversation_url = data.get("conversation_url")

            print(f"✅ Tavus conversation created: {conversation_id}")
            print(f"   URL: {conversation_url}")

            return {
                "conversation_id": conversation_id,
                "conversation_url": conversation_url
            }

    async def stop(self, conversation_id: str):
        """Stop Tavus conversation"""
        import httpx

        if not conversation_id:
            return

        print(f"🛑 Stopping Tavus conversation: {conversation_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"https://tavusapi.com/v2/conversations/{conversation_id}",
                headers={"x-api-key": self.tavus_api_key}
            )

            if response.status_code == 200:
                print(f"✅ Tavus conversation stopped")
            else:
                print(f"⚠️  Failed to stop Tavus conversation: {response.text}")
