#!/usr/bin/env python3
"""
Conversation API Endpoints for Call Center
Handles real-time conversations with WebSocket and REST endpoints
"""

import logging
import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from pydantic import BaseModel

# Handle both relative and absolute imports
try:
    from .conversation_manager import (
        get_conversation_manager,
        remove_conversation_manager,
        ConversationManager,
    )
    from .openai_personas import PersonaType, get_persona_manager
except ImportError:
    from conversation_manager import (
        get_conversation_manager,
        remove_conversation_manager,
        ConversationManager,
    )
    from openai_personas import PersonaType, get_persona_manager

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MessageRequest(BaseModel):
    """Request to send a message in a conversation"""
    message: str
    language: Optional[str] = "en"


class PersonaSwitchRequest(BaseModel):
    """Request to switch to a different persona"""
    persona: str  # "reception", "sales", "complaints"


class ConversationResponse(BaseModel):
    """Response with assistant message"""
    assistant_response: str
    persona: str
    timestamp: datetime


class TranscriptResponse(BaseModel):
    """Response with full transcript"""
    call_id: str
    messages: list
    statistics: dict


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@router.post("/{call_id}/message")
async def send_message(
    call_id: str,
    request: MessageRequest,
    customer_name: Optional[str] = Query("Customer")
) -> ConversationResponse:
    """
    Send a message in an ongoing conversation
    Automatically routes to appropriate persona based on message content
    """
    try:
        # Get or create conversation manager
        manager = get_conversation_manager(call_id, customer_name, request.language)

        # Get OpenAI response (will auto-detect persona)
        response = await manager.get_response(request.message)

        return ConversationResponse(
            assistant_response=response,
            persona=manager.current_persona.value,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error sending message to call {call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{call_id}/switch-persona")
async def switch_persona(
    call_id: str,
    request: PersonaSwitchRequest,
) -> dict:
    """Manually switch to a different persona during conversation"""
    try:
        manager = get_conversation_manager(call_id)

        # Validate persona type
        try:
            persona = PersonaType(request.persona.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid persona. Must be one of: {[p.value for p in PersonaType]}"
            )

        # Switch persona
        manager.switch_persona(persona)

        # Get greeting from new persona
        persona_info = get_persona_manager().get_persona_info(persona)

        return {
            "success": True,
            "new_persona": persona.value,
            "persona_name": persona_info["name"],
            "persona_name_ar": persona_info["name_ar"],
            "message": f"Switched to {persona_info['name']} from {persona_info['department']}"
        }
    except Exception as e:
        logger.error(f"Error switching persona for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}/transcript")
async def get_transcript(call_id: str) -> TranscriptResponse:
    """Get the full conversation transcript for a call"""
    try:
        manager = get_conversation_manager(call_id)

        return TranscriptResponse(
            call_id=call_id,
            messages=manager.get_transcript(),
            statistics=manager.get_statistics(),
        )
    except Exception as e:
        logger.error(f"Error getting transcript for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}/stats")
async def get_conversation_stats(call_id: str) -> dict:
    """Get conversation statistics"""
    try:
        manager = get_conversation_manager(call_id)
        return manager.get_statistics()
    except Exception as e:
        logger.error(f"Error getting stats for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{call_id}")
async def end_conversation(call_id: str) -> dict:
    """End conversation and clean up resources"""
    try:
        manager = get_conversation_manager(call_id)

        # Get final transcript
        transcript = manager.to_call_transcript()

        # Remove conversation from memory
        remove_conversation_manager(call_id)

        logger.info(f"Ended conversation for call {call_id}")

        return {
            "success": True,
            "message": "Conversation ended",
            "call_id": call_id,
            "transcript_saved": True,
            "total_messages": transcript.total_messages,
        }
    except Exception as e:
        logger.error(f"Error ending conversation for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

# In-memory WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, call_id: str, websocket: WebSocket):
        await websocket.accept()
        if call_id not in self.active_connections:
            self.active_connections[call_id] = []
        self.active_connections[call_id].append(websocket)
        logger.info(f"WebSocket connected for call {call_id}")

    async def disconnect(self, call_id: str, websocket: WebSocket):
        if call_id in self.active_connections:
            self.active_connections[call_id].remove(websocket)
            if not self.active_connections[call_id]:
                del self.active_connections[call_id]
        logger.info(f"WebSocket disconnected for call {call_id}")

    async def broadcast(self, call_id: str, message: dict):
        """Broadcast message to all connected clients for a call"""
        if call_id in self.active_connections:
            for connection in self.active_connections[call_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


connection_manager = ConnectionManager()


@router.websocket("/ws/{call_id}")
async def websocket_conversation_endpoint(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for real-time conversation
    Handles bi-directional streaming of messages
    """
    await connection_manager.connect(call_id, websocket)

    try:
        # Send connection confirmation
        await connection_manager.send_personal(
            websocket,
            {
                "event": "connected",
                "call_id": call_id,
                "message": "Connected to Call Center conversation",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Send initial greeting
        manager = get_conversation_manager(call_id)
        greeting = manager.messages[0].content if manager.messages else "Welcome to Ornina Call Center"

        await connection_manager.send_personal(
            websocket,
            {
                "event": "greeting",
                "call_id": call_id,
                "persona": "reception",
                "message": greeting,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")
            language = message_data.get("language", "en")

            if not user_message:
                await connection_manager.send_personal(
                    websocket,
                    {"event": "error", "message": "Empty message"}
                )
                continue

            # Broadcast user message to all clients
            await connection_manager.broadcast(
                call_id,
                {
                    "event": "user_message",
                    "call_id": call_id,
                    "message": user_message,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Get response from conversation manager
            try:
                manager = get_conversation_manager(call_id, language=language)
                response = await manager.get_response(user_message)

                # Broadcast assistant response
                await connection_manager.broadcast(
                    call_id,
                    {
                        "event": "assistant_message",
                        "call_id": call_id,
                        "message": response,
                        "persona": manager.current_persona.value,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                await connection_manager.broadcast(
                    call_id,
                    {
                        "event": "error",
                        "message": f"Error: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        await connection_manager.disconnect(call_id, websocket)
        logger.info(f"Client disconnected from call {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        await connection_manager.disconnect(call_id, websocket)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "router",
    "connection_manager",
]
