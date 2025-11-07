#!/usr/bin/env python3
"""
API to retrieve conversation transcripts for frontend
Can be used with Flask, FastAPI, or any web framework
"""
import os
from typing import List, Dict, Optional
from conversation_logger import ConversationLogger
from dotenv import load_dotenv

load_dotenv()

class TranscriptAPI:
    def __init__(self):
        self.logger = ConversationLogger()

    def get_conversation_transcript(
        self,
        conversation_id: str,
        format: str = "json"  # json, text, html
    ) -> Dict:
        """
        Get full conversation transcript by conversation_id

        Returns:
        {
            "conversation_id": "room-123",
            "message_count": 10,
            "messages": [
                {
                    "role": "user",
                    "content": "مرحباً",
                    "timestamp": "2025-11-05T09:00:00",
                    "message_id": "uuid-123"
                },
                ...
            ],
            "transcript_text": "User: مرحباً\nAgent: أهلاً بك...",
            "transcript_html": "<div>...</div>"
        }
        """
        messages = self.logger.get_messages_by_conversation(conversation_id, limit=1000)

        if not messages:
            return {
                "error": "No messages found",
                "conversation_id": conversation_id,
                "message_count": 0,
                "messages": []
            }

        # Format as different types
        transcript_text = self._format_as_text(messages)
        transcript_html = self._format_as_html(messages)

        return {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "messages": messages,
            "transcript_text": transcript_text,
            "transcript_html": transcript_html
        }

    def get_room_transcript(
        self,
        room_name: str,
        limit: int = 100
    ) -> Dict:
        """Get recent messages from a specific room"""
        messages = self.logger.get_messages_by_room(room_name, limit=limit)

        return {
            "room_name": room_name,
            "message_count": len(messages),
            "messages": messages,
            "transcript_text": self._format_as_text(messages)
        }

    def get_user_transcript(
        self,
        user_phone: str,
        limit: int = 100
    ) -> Dict:
        """Get all messages from a specific user"""
        messages = self.logger.get_user_messages(user_phone, limit=limit)

        return {
            "user_phone": user_phone,
            "message_count": len(messages),
            "messages": messages,
            "transcript_text": self._format_as_text(messages)
        }

    def _format_as_text(self, messages: List[Dict]) -> str:
        """Format messages as plain text transcript"""
        lines = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Agent"
            timestamp = msg.get("timestamp", "")
            content = msg.get("content", "")
            lines.append(f"[{timestamp}] {role}: {content}")
        return "\n".join(lines)

    def _format_as_html(self, messages: List[Dict]) -> str:
        """Format messages as HTML transcript"""
        html_parts = ['<div class="conversation-transcript">']

        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            role_class = "user-message" if role == "user" else "agent-message"
            role_label = "المستخدم" if role == "user" else "الوكيل"

            html_parts.append(f'''
            <div class="message {role_class}">
                <div class="message-header">
                    <span class="role">{role_label}</span>
                    <span class="timestamp">{timestamp}</span>
                </div>
                <div class="message-content">{content}</div>
            </div>
            ''')

        html_parts.append('</div>')
        return '\n'.join(html_parts)

# Flask API example
def create_flask_app():
    """Example Flask app with transcript endpoints"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend

    api = TranscriptAPI()

    @app.route('/api/transcript/<conversation_id>', methods=['GET'])
    def get_transcript(conversation_id):
        """Get transcript by conversation ID"""
        format_type = request.args.get('format', 'json')
        result = api.get_conversation_transcript(conversation_id, format=format_type)
        return jsonify(result)

    @app.route('/api/transcript/room/<room_name>', methods=['GET'])
    def get_room_transcript(room_name):
        """Get transcript by room name"""
        limit = request.args.get('limit', 100, type=int)
        result = api.get_room_transcript(room_name, limit=limit)
        return jsonify(result)

    @app.route('/api/transcript/user/<user_phone>', methods=['GET'])
    def get_user_transcript(user_phone):
        """Get all messages from a user"""
        limit = request.args.get('limit', 100, type=int)
        result = api.get_user_transcript(user_phone, limit=limit)
        return jsonify(result)

    @app.route('/api/conversations/recent', methods=['GET'])
    def get_recent_conversations():
        """Get list of recent conversations"""
        # This would need a new method in ConversationLogger
        return jsonify({
            "message": "Not implemented yet"
        })

    return app

# FastAPI example
def create_fastapi_app():
    """Example FastAPI app with transcript endpoints"""
    from fastapi import FastAPI, Query
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="Ornina Transcript API")

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = TranscriptAPI()

    @app.get("/api/transcript/{conversation_id}")
    async def get_transcript(
        conversation_id: str,
        format: str = Query("json", description="Format: json, text, or html")
    ):
        """Get transcript by conversation ID"""
        return api.get_conversation_transcript(conversation_id, format=format)

    @app.get("/api/transcript/room/{room_name}")
    async def get_room_transcript(
        room_name: str,
        limit: int = Query(100, description="Max number of messages")
    ):
        """Get transcript by room name"""
        return api.get_room_transcript(room_name, limit=limit)

    @app.get("/api/transcript/user/{user_phone}")
    async def get_user_transcript(
        user_phone: str,
        limit: int = Query(100, description="Max number of messages")
    ):
        """Get all messages from a user"""
        return api.get_user_transcript(user_phone, limit=limit)

    return app

if __name__ == "__main__":
    # Test the API
    print("Testing Transcript API...\n")

    api = TranscriptAPI()

    # Test getting a conversation
    result = api.get_conversation_transcript("test-session-001")

    print(f"Conversation ID: {result.get('conversation_id')}")
    print(f"Messages: {result.get('message_count')}")
    print("\nTranscript (Text):")
    print(result.get('transcript_text', 'No messages'))
    print("\n" + "="*60)

    # To run Flask server:
    # flask_app = create_flask_app()
    # flask_app.run(host='0.0.0.0', port=5000)

    # To run FastAPI server:
    # import uvicorn
    # fastapi_app = create_fastapi_app()
    # uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
