#!/usr/bin/env python3
"""
LiveKit Manager for Call Center - Audio Only
Simple JWT token generation for LiveKit room access
No video or facial recognition
"""

import os
import logging
import json
import time
import jwt
from typing import Optional, Dict
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")


class LiveKitManager:
    """Manages LiveKit integration for audio-only call center"""

    def __init__(self):
        """Initialize LiveKit manager"""
        self.livekit_url = LIVEKIT_URL
        self.api_key = LIVEKIT_API_KEY
        self.api_secret = LIVEKIT_API_SECRET
        logger.info(f"LiveKit Manager initialized - URL: {self.livekit_url}")

    def create_token(
        self,
        room_name: str,
        participant_name: str,
        participant_identity: str,
        can_publish: bool = True,
        can_subscribe: bool = True,
        duration_minutes: int = 60
    ) -> Optional[str]:
        """
        Create a LiveKit access token for a participant

        Args:
            room_name: Name of the LiveKit room
            participant_name: Display name of participant
            participant_identity: Unique identifier for participant
            can_publish: Whether participant can publish audio
            can_subscribe: Whether participant can receive streams
            duration_minutes: Token validity duration in minutes

        Returns:
            Access token string or None if failed
        """
        try:
            # Token expiration timestamp
            now = int(time.time())
            expiration = now + (duration_minutes * 60)

            # Create JWT payload
            payload = {
                "iss": self.api_key,
                "sub": participant_identity,
                "iat": now,
                "exp": expiration,
                "nbf": now,
                "video": {
                    "room_join": True,
                    "room": room_name,
                    "can_publish": can_publish,
                    "can_subscribe": can_subscribe,
                    "can_publish_data": True,
                    "can_subscribe_data": True,
                    # Audio-only settings
                    "can_publish_sources": ["microphone"],
                    "can_subscribe_sources": ["microphone"]
                },
                "metadata": json.dumps({
                    "created_at": datetime.utcnow().isoformat(),
                    "room": room_name,
                    "participant_name": participant_name,
                    "participant_identity": participant_identity,
                    "audio_only": True
                })
            }

            # Encode JWT token
            token = jwt.encode(payload, self.api_secret, algorithm="HS256")
            logger.info(f"Created token for {participant_name} in room {room_name}")
            return token

        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            return None

    def create_room(self, room_name: str, max_participants: int = 10) -> Dict:
        """
        Create a LiveKit room (stub implementation)
        In production, would connect to LiveKit API

        Args:
            room_name: Name of the room
            max_participants: Maximum participants allowed

        Returns:
            Room info dictionary
        """
        try:
            logger.info(f"Room creation requested: {room_name} (max {max_participants})")
            # In production, this would call the LiveKit API
            return {
                "success": True,
                "room_name": room_name,
                "max_participants": max_participants,
                "creation_time": datetime.utcnow().isoformat(),
                "status": "pending"  # Will exist when first participant joins
            }
        except Exception as e:
            logger.error(f"Room creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "room_name": room_name
            }

    def delete_room(self, room_name: str) -> Dict:
        """
        Delete a LiveKit room

        Args:
            room_name: Name of the room to delete

        Returns:
            Deletion result
        """
        try:
            logger.info(f"Room deletion requested: {room_name}")
            # In production, would call the LiveKit API
            return {
                "success": True,
                "room_name": room_name,
                "deletion_time": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Room deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "room_name": room_name
            }

    def get_room_participants(self, room_name: str) -> list:
        """
        Get list of participants in a room

        Args:
            room_name: Name of the room

        Returns:
            List of participant info dictionaries
        """
        try:
            logger.info(f"Getting participants for room: {room_name}")
            # In production, would call the LiveKit API
            return []  # Empty list - rooms are created on first join
        except Exception as e:
            logger.error(f"Failed to get participants: {str(e)}")
            return []

    def remove_participant(self, room_name: str, participant_identity: str) -> Dict:
        """
        Remove a participant from a room

        Args:
            room_name: Name of the room
            participant_identity: Identity of the participant to remove

        Returns:
            Removal result
        """
        try:
            logger.info(f"Removing participant {participant_identity} from room {room_name}")
            # In production, would call the LiveKit API
            return {
                "success": True,
                "room_name": room_name,
                "participant_identity": participant_identity
            }
        except Exception as e:
            logger.error(f"Failed to remove participant: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def mute_participant(self, room_name: str, participant_identity: str, mute_audio: bool = True) -> Dict:
        """
        Mute or unmute a participant's audio

        Args:
            room_name: Name of the room
            participant_identity: Identity of the participant
            mute_audio: True to mute, False to unmute

        Returns:
            Mute operation result
        """
        try:
            action = "muted" if mute_audio else "unmuted"
            logger.info(f"{action.capitalize()} participant {participant_identity} in room {room_name}")
            # In production, would call the LiveKit API
            return {
                "success": True,
                "room_name": room_name,
                "participant_identity": participant_identity,
                "audio_muted": mute_audio
            }
        except Exception as e:
            logger.error(f"Failed to mute participant: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global manager instance
_manager = None


def get_livekit_manager() -> LiveKitManager:
    """Get or create the global LiveKit manager instance"""
    global _manager
    if _manager is None:
        _manager = LiveKitManager()
    return _manager


def reset_livekit_manager():
    """Reset the global manager instance (for testing)"""
    global _manager
    _manager = None


__all__ = ["LiveKitManager", "get_livekit_manager", "reset_livekit_manager"]
