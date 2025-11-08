#!/usr/bin/env python3
"""
API to save conversation transcripts to database
Handles storing messages from frontend during video calls
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from conversation_logger import ConversationLogger
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class TranscriptSaveAPI:
    """API for saving transcripts to database"""

    def __init__(self):
        self.logger_service = ConversationLogger()

    def save_message(
        self,
        conversation_id: str,
        room_name: str,
        role: str,  # "user" or "assistant"
        content: str,
        user_phone: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Save a single message to the database

        Args:
            conversation_id: Unique conversation identifier
            room_name: LiveKit room name
            role: Message role (user or assistant)
            content: Message text
            user_phone: User's phone number (optional)
            metadata: Additional metadata (optional)

        Returns:
            {
                "success": True/False,
                "message_id": "uuid",
                "conversation_id": "room-123",
                "timestamp": "2025-11-08T10:30:00"
            }
        """
        try:
            # Save message using ConversationLogger
            message_id = self.logger_service.log_message(
                conversation_id=conversation_id,
                room_name=room_name,
                user_phone=user_phone,
                role=role,
                content=content,
                metadata=metadata or {}
            )

            logger.info(f"✅ Message saved: {conversation_id} - {role}: {content[:50]}...")

            return {
                "success": True,
                "message_id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "timestamp": datetime.now().isoformat(),
                "message_preview": content[:100]
            }

        except Exception as e:
            logger.error(f"❌ Failed to save message: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }

    def save_batch_messages(
        self,
        conversation_id: str,
        room_name: str,
        messages: List[Dict],
        user_phone: Optional[str] = None
    ) -> Dict:
        """
        Save multiple messages at once

        Args:
            conversation_id: Unique conversation identifier
            room_name: LiveKit room name
            messages: List of messages to save
                [
                    {
                        "role": "user",
                        "content": "مرحباً",
                        "timestamp": "2025-11-08T10:30:00" (optional)
                    },
                    ...
                ]
            user_phone: User's phone number (optional)

        Returns:
            {
                "success": True/False,
                "conversation_id": "room-123",
                "saved_count": 5,
                "failed_count": 0,
                "message_ids": ["uuid1", "uuid2", ...]
            }
        """
        saved_count = 0
        failed_count = 0
        message_ids = []

        for msg in messages:
            try:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if not content.strip():
                    logger.warning("Skipping empty message")
                    continue

                # Save individual message
                result = self.save_message(
                    conversation_id=conversation_id,
                    room_name=room_name,
                    role=role,
                    content=content,
                    user_phone=user_phone,
                    metadata=msg.get("metadata", {})
                )

                if result["success"]:
                    saved_count += 1
                    message_ids.append(result["message_id"])
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"Error saving individual message: {e}")
                failed_count += 1

        logger.info(f"📊 Batch save: {saved_count} saved, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "conversation_id": conversation_id,
            "saved_count": saved_count,
            "failed_count": failed_count,
            "message_ids": message_ids,
            "timestamp": datetime.now().isoformat()
        }

    def end_conversation(
        self,
        conversation_id: str,
        duration_seconds: Optional[int] = None,
        summary: Optional[str] = None
    ) -> Dict:
        """
        Mark conversation as ended and save final metadata

        Args:
            conversation_id: Conversation identifier
            duration_seconds: Duration of the call in seconds
            summary: Summary of the conversation

        Returns:
            {
                "success": True/False,
                "conversation_id": "room-123",
                "message_count": 15
            }
        """
        try:
            # Get conversation message count
            conversation = self.logger_service.get_conversation(conversation_id)
            message_count = len(conversation.get("messages", [])) if conversation else 0

            logger.info(
                f"✅ Conversation ended: {conversation_id} "
                f"({message_count} messages, {duration_seconds}s)"
            )

            return {
                "success": True,
                "conversation_id": conversation_id,
                "message_count": message_count,
                "duration_seconds": duration_seconds,
                "summary": summary,
                "ended_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Failed to end conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }


# FastAPI endpoints
def create_fastapi_save_app():
    """Create FastAPI app for saving transcripts"""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List

    app = FastAPI(title="Ornina Transcript Save API")

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = TranscriptSaveAPI()

    # Pydantic models for request validation
    class MessageRequest(BaseModel):
        role: str  # "user" or "assistant"
        content: str
        metadata: Optional[Dict] = None

    class BatchMessagesRequest(BaseModel):
        messages: List[MessageRequest]
        user_phone: Optional[str] = None

    class EndConversationRequest(BaseModel):
        duration_seconds: Optional[int] = None
        summary: Optional[str] = None

    @app.post("/api/save-message/{conversation_id}/{room_name}")
    async def save_message(
        conversation_id: str,
        room_name: str,
        message: MessageRequest,
        user_phone: Optional[str] = None
    ):
        """Save a single message to database"""
        result = api.save_message(
            conversation_id=conversation_id,
            room_name=room_name,
            role=message.role,
            content=message.content,
            user_phone=user_phone,
            metadata=message.metadata
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    @app.post("/api/save-messages/{conversation_id}/{room_name}")
    async def save_batch_messages(
        conversation_id: str,
        room_name: str,
        batch: BatchMessagesRequest
    ):
        """Save multiple messages at once"""
        messages = [msg.dict() for msg in batch.messages]

        result = api.save_batch_messages(
            conversation_id=conversation_id,
            room_name=room_name,
            messages=messages,
            user_phone=batch.user_phone
        )

        if result["failed_count"] > 0 and result["saved_count"] == 0:
            raise HTTPException(status_code=500, detail="Failed to save any messages")

        return result

    @app.post("/api/end-conversation/{conversation_id}")
    async def end_conversation(
        conversation_id: str,
        request: EndConversationRequest
    ):
        """Mark conversation as ended"""
        result = api.end_conversation(
            conversation_id=conversation_id,
            duration_seconds=request.duration_seconds,
            summary=request.summary
        )

        return result

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "service": "transcript-save-api"}

    return app


# Flask endpoints
def create_flask_save_app():
    """Create Flask app for saving transcripts"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)

    api = TranscriptSaveAPI()

    @app.route('/api/save-message/<conversation_id>/<room_name>', methods=['POST'])
    def save_message(conversation_id, room_name):
        """Save a single message"""
        data = request.get_json()

        result = api.save_message(
            conversation_id=conversation_id,
            room_name=room_name,
            role=data.get('role', 'user'),
            content=data.get('content', ''),
            user_phone=data.get('user_phone'),
            metadata=data.get('metadata')
        )

        return jsonify(result), 200 if result['success'] else 500

    @app.route('/api/save-messages/<conversation_id>/<room_name>', methods=['POST'])
    def save_batch_messages(conversation_id, room_name):
        """Save multiple messages"""
        data = request.get_json()

        result = api.save_batch_messages(
            conversation_id=conversation_id,
            room_name=room_name,
            messages=data.get('messages', []),
            user_phone=data.get('user_phone')
        )

        return jsonify(result), 200 if result['success'] else 500

    @app.route('/api/end-conversation/<conversation_id>', methods=['POST'])
    def end_conversation(conversation_id):
        """Mark conversation as ended"""
        data = request.get_json() or {}

        result = api.end_conversation(
            conversation_id=conversation_id,
            duration_seconds=data.get('duration_seconds'),
            summary=data.get('summary')
        )

        return jsonify(result), 200

    return app


if __name__ == "__main__":
    # Test the API
    print("Testing Transcript Save API...\n")

    api = TranscriptSaveAPI()

    # Test saving a message
    result = api.save_message(
        conversation_id="ornina-test-001",
        room_name="test-room",
        role="user",
        content="مرحبا، كيف حالك؟",
        metadata={"source": "test"}
    )

    print("Save Message Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message ID: {result.get('message_id')}")
    print(f"  Timestamp: {result.get('timestamp')}")

    # Test ending conversation
    print("\n" + "="*60)
    end_result = api.end_conversation(
        conversation_id="ornina-test-001",
        duration_seconds=300,
        summary="Test conversation"
    )

    print("End Conversation Result:")
    print(f"  Success: {end_result['success']}")
    print(f"  Message Count: {end_result.get('message_count')}")
    print(f"  Duration: {end_result.get('duration_seconds')}s")
