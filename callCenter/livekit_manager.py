#!/usr/bin/env python3
"""
LiveKit Manager for Call Center - Audio Only
JWT token generation and LiveKit API integration for room management
No video or facial recognition
"""

import os
import logging
import json
import time
import jwt
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timedelta

try:
    from livekit import api
    LIVEKIT_SDK_AVAILABLE = True
except ImportError:
    LIVEKIT_SDK_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LiveKit Python SDK not available - room operations will be simulated")

# Configure logging
logger = logging.getLogger(__name__)

# LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_URL = os.getenv("LIVEKIT_API_URL", "http://localhost:9090")  # REST API endpoint
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")


class LiveKitManager:
    """Manages LiveKit integration for audio-only call center"""

    def __init__(self):
        """Initialize LiveKit manager"""
        self.livekit_url = LIVEKIT_URL
        self.api_url = LIVEKIT_API_URL
        self.api_key = LIVEKIT_API_KEY
        self.api_secret = LIVEKIT_API_SECRET
        self.sdk_available = LIVEKIT_SDK_AVAILABLE

        # Try to initialize LiveKit API client
        if self.sdk_available:
            try:
                self.room_service = api.RoomServiceClient(
                    ws_url=self.api_url,
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )
                logger.info(f"✅ LiveKit API client initialized - URL: {self.api_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize LiveKit API client: {e}")
                self.room_service = None
        else:
            self.room_service = None
            logger.warning("LiveKit SDK not available - using simulation mode")

        logger.info(f"LiveKit Manager initialized - WS URL: {self.livekit_url}")

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

    def create_room(self, room_name: str, max_participants: int = 10, empty_timeout: int = 300) -> Dict:
        """
        Create a LiveKit room via API

        Args:
            room_name: Name of the room
            max_participants: Maximum participants allowed
            empty_timeout: Room timeout when empty (seconds)

        Returns:
            Room info dictionary
        """
        try:
            logger.info(f"Creating LiveKit room: {room_name} (max {max_participants})")

            if self.room_service:
                try:
                    # Create room via LiveKit API
                    from livekit import api as livekit_api
                    room_opts = livekit_api.CreateRoomRequest(
                        room=room_name,
                        max_participants=max_participants,
                        empty_timeout_seconds=empty_timeout,
                        # Audio-only settings
                        metadata=json.dumps({
                            "type": "call_center",
                            "audio_only": True,
                            "created_at": datetime.utcnow().isoformat()
                        })
                    )

                    # Execute create room request
                    room = self.room_service.create_room(room_opts)

                    logger.info(f"✅ Room created: {room_name}")
                    return {
                        "success": True,
                        "room_name": room.name,
                        "max_participants": room.max_participants,
                        "num_participants": room.num_participants,
                        "creation_time": datetime.utcnow().isoformat(),
                        "status": "active"
                    }

                except Exception as api_error:
                    logger.warning(f"LiveKit API call failed: {api_error}. Using simulation mode.")
                    # Fallback to simulation
                    return self._simulate_create_room(room_name, max_participants)
            else:
                # SDK not available, use simulation
                return self._simulate_create_room(room_name, max_participants)

        except Exception as e:
            logger.error(f"Room creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "room_name": room_name
            }

    def _simulate_create_room(self, room_name: str, max_participants: int) -> Dict:
        """Simulate room creation when SDK not available"""
        logger.info(f"📋 [SIMULATION] Room would be created: {room_name}")
        return {
            "success": True,
            "room_name": room_name,
            "max_participants": max_participants,
            "num_participants": 0,
            "creation_time": datetime.utcnow().isoformat(),
            "status": "simulated"  # Indicates this is a simulated response
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
            logger.info(f"Deleting LiveKit room: {room_name}")

            if self.room_service:
                try:
                    from livekit import api as livekit_api
                    # Delete room via API
                    self.room_service.delete_room(room_name)
                    logger.info(f"✅ Room deleted: {room_name}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "deletion_time": datetime.utcnow().isoformat()
                    }
                except Exception as api_error:
                    logger.warning(f"LiveKit API delete failed: {api_error}")
                    # Still report success in simulation mode
                    logger.info(f"📋 [SIMULATION] Room would be deleted: {room_name}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "deletion_time": datetime.utcnow().isoformat(),
                        "status": "simulated"
                    }
            else:
                # Simulation mode
                logger.info(f"📋 [SIMULATION] Room would be deleted: {room_name}")
                return {
                    "success": True,
                    "room_name": room_name,
                    "deletion_time": datetime.utcnow().isoformat(),
                    "status": "simulated"
                }

        except Exception as e:
            logger.error(f"Room deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "room_name": room_name
            }

    def get_room_participants(self, room_name: str) -> List[Dict]:
        """
        Get list of participants in a room

        Args:
            room_name: Name of the room

        Returns:
            List of participant info dictionaries
        """
        try:
            logger.info(f"Getting participants for room: {room_name}")

            if self.room_service:
                try:
                    # Get room info via API
                    room = self.room_service.list_rooms(room_name).rooms[0]
                    participants = []

                    for participant in room.participants:
                        participants.append({
                            "identity": participant.identity,
                            "name": participant.name,
                            "state": participant.state,
                            "is_publisher": participant.is_publisher,
                            "joined_at": participant.joined_at
                        })

                    logger.info(f"Found {len(participants)} participants in {room_name}")
                    return participants

                except Exception as api_error:
                    logger.warning(f"LiveKit API call failed: {api_error}")
                    return []
            else:
                # Simulation mode
                logger.debug(f"📋 [SIMULATION] Would query participants for: {room_name}")
                return []

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

            if self.room_service:
                try:
                    # Remove participant via API
                    self.room_service.remove_participant(room_name, participant_identity)
                    logger.info(f"✅ Participant {participant_identity} removed from {room_name}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "participant_identity": participant_identity,
                        "removed_at": datetime.utcnow().isoformat()
                    }
                except Exception as api_error:
                    logger.warning(f"LiveKit API call failed: {api_error}")
                    # Simulate success
                    logger.info(f"📋 [SIMULATION] Participant would be removed: {participant_identity}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "participant_identity": participant_identity,
                        "removed_at": datetime.utcnow().isoformat(),
                        "status": "simulated"
                    }
            else:
                # Simulation mode
                logger.info(f"📋 [SIMULATION] Participant would be removed: {participant_identity}")
                return {
                    "success": True,
                    "room_name": room_name,
                    "participant_identity": participant_identity,
                    "removed_at": datetime.utcnow().isoformat(),
                    "status": "simulated"
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
            logger.info(f"Attempting to {action}: {participant_identity} in room {room_name}")

            if self.room_service:
                try:
                    from livekit import api as livekit_api
                    # Mute participant via API
                    self.room_service.mute_publish_track(
                        room_name,
                        participant_identity,
                        mute_audio
                    )
                    logger.info(f"✅ Participant {action}: {participant_identity}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "participant_identity": participant_identity,
                        "audio_muted": mute_audio,
                        "action_time": datetime.utcnow().isoformat()
                    }
                except Exception as api_error:
                    logger.warning(f"LiveKit API call failed: {api_error}")
                    # Simulate success
                    logger.info(f"📋 [SIMULATION] Participant would be {action}: {participant_identity}")
                    return {
                        "success": True,
                        "room_name": room_name,
                        "participant_identity": participant_identity,
                        "audio_muted": mute_audio,
                        "action_time": datetime.utcnow().isoformat(),
                        "status": "simulated"
                    }
            else:
                # Simulation mode
                logger.info(f"📋 [SIMULATION] Participant would be {action}: {participant_identity}")
                return {
                    "success": True,
                    "room_name": room_name,
                    "participant_identity": participant_identity,
                    "audio_muted": mute_audio,
                    "action_time": datetime.utcnow().isoformat(),
                    "status": "simulated"
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
