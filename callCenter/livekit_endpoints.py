#!/usr/bin/env python3
"""
LiveKit API Endpoints for Call Center
Provides token generation and room management for audio calls
"""

import logging
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel

# Use absolute imports - Docker runs with all files in /app
from livekit_manager import get_livekit_manager

logger = logging.getLogger(__name__)


class RoomTokenRequest(BaseModel):
    """Request model for getting a LiveKit room token"""
    room_name: str
    participant_name: str
    participant_identity: str


class RoomTokenResponse(BaseModel):
    """Response model for room token"""
    token: str
    livekit_url: str
    room_name: str
    participant_name: str


async def register_livekit_endpoints(app):
    """
    Register LiveKit endpoints with FastAPI app

    Args:
        app: FastAPI application instance
    """

    @app.post("/api/room/token")
    async def get_room_token(request: RoomTokenRequest) -> RoomTokenResponse:
        """
        Generate a LiveKit access token for a participant to join a room

        This endpoint creates a JWT token that allows a client to connect to
        a LiveKit room for audio/video streaming.

        Args:
            request: Room token request with room name, participant name, and identity

        Returns:
            Token and LiveKit server URL

        Raises:
            HTTPException: If token generation fails
        """
        try:
            logger.info(
                f"Generating token for room: {request.room_name}, "
                f"participant: {request.participant_name}"
            )

            manager = get_livekit_manager()

            # Generate token
            token = manager.create_token(
                room_name=request.room_name,
                participant_name=request.participant_name,
                participant_identity=request.participant_identity,
                can_publish=True,
                can_subscribe=True,
                duration_minutes=60
            )

            if not token:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate LiveKit token"
                )

            # Get LiveKit URL from manager
            livekit_url = manager.livekit_url

            logger.info(f"Token generated successfully for {request.participant_name}")

            return RoomTokenResponse(
                token=token,
                livekit_url=livekit_url,
                room_name=request.room_name,
                participant_name=request.participant_name
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Token generation failed: {str(e)}"
            )


    @app.post("/api/room/create")
    async def create_room(room_name: str, max_participants: int = 10) -> Dict:
        """
        Create a new LiveKit room for a call

        Args:
            room_name: Name of the room to create
            max_participants: Maximum number of participants allowed

        Returns:
            Room creation result
        """
        try:
            logger.info(f"Creating room: {room_name}")

            manager = get_livekit_manager()
            result = manager.create_room(room_name, max_participants)

            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Failed to create room")
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating room: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Room creation failed: {str(e)}"
            )


    @app.delete("/api/room/{room_name}")
    async def delete_room(room_name: str) -> Dict:
        """
        Delete a LiveKit room and all its participants

        Args:
            room_name: Name of the room to delete

        Returns:
            Deletion result
        """
        try:
            logger.info(f"Deleting room: {room_name}")

            manager = get_livekit_manager()
            result = manager.delete_room(room_name)

            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Failed to delete room")
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting room: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Room deletion failed: {str(e)}"
            )


    @app.get("/api/room/{room_name}/participants")
    async def get_room_participants(room_name: str) -> Dict:
        """
        Get list of participants in a room

        Args:
            room_name: Name of the room

        Returns:
            List of participants in the room
        """
        try:
            logger.info(f"Getting participants for room: {room_name}")

            manager = get_livekit_manager()
            participants = manager.get_room_participants(room_name)

            return {
                "room_name": room_name,
                "participants": participants,
                "count": len(participants)
            }

        except Exception as e:
            logger.error(f"Error getting participants: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get participants: {str(e)}"
            )


    @app.post("/api/room/{room_name}/mute")
    async def mute_participant(
        room_name: str,
        participant_identity: str,
        mute_audio: bool = True
    ) -> Dict:
        """
        Mute a participant's audio in a room

        Args:
            room_name: Name of the room
            participant_identity: Identity of the participant
            mute_audio: Whether to mute (True) or unmute (False)

        Returns:
            Mute operation result
        """
        try:
            logger.info(
                f"Muting participant {participant_identity} in room {room_name}: {mute_audio}"
            )

            manager = get_livekit_manager()
            result = manager.mute_participant(
                room_name,
                participant_identity,
                mute_audio=mute_audio
            )

            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Failed to mute participant")
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error muting participant: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Mute operation failed: {str(e)}"
            )


    logger.info("LiveKit endpoints registered successfully")


__all__ = ["register_livekit_endpoints", "RoomTokenRequest", "RoomTokenResponse"]
