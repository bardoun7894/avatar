#!/usr/bin/env python3
"""
Conversation Logger - Save conversations to Supabase
Uses individual message tracking for better history
"""
import os
import uuid
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class ConversationLogger:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def save_message(
        self,
        conversation_id: str,
        role: str,  # 'user' or 'assistant'
        content: str,
        room_name: str = None,
        user_phone: str = None,
        metadata: dict = None
    ) -> dict:
        """Save a single message to Supabase"""
        try:
            message = {
                "message_id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "room_name": room_name,
                "user_phone": user_phone,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            response = self.supabase.table('messages').insert(message).execute()

            if response.data:
                return response.data[0]
            return message

        except Exception as e:
            print(f"⚠️  Error saving message: {e}")
            return None

    def save_conversation(
        self,
        room_name: str,
        user_message: str,
        ai_response: str,
        language: str = "ar",
        session_id: str = None,
        user_phone: str = None
    ) -> dict:
        """Save a conversation turn (user message + AI response)"""
        try:
            conversation_id = session_id or room_name

            # Save user message
            user_msg = self.save_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                room_name=room_name,
                user_phone=user_phone,
                metadata={"language": language}
            )

            # Save AI response
            ai_msg = self.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response,
                room_name=room_name,
                user_phone=user_phone,
                metadata={"language": language}
            )

            return {"user": user_msg, "assistant": ai_msg}

        except Exception as e:
            print(f"⚠️  Error saving conversation: {e}")
            return None

    def get_messages_by_conversation(self, conversation_id: str, limit: int = 50):
        """Get all messages for a conversation"""
        try:
            response = self.supabase.table('messages')\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("timestamp", desc=False)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching messages: {e}")
            return []

    def get_messages_by_room(self, room_name: str, limit: int = 20):
        """Get recent messages for a room"""
        try:
            response = self.supabase.table('messages')\
                .select("*")\
                .eq("room_name", room_name)\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching messages: {e}")
            return []

    def get_user_messages(self, user_phone: str, limit: int = 20):
        """Get messages for a specific user by phone"""
        try:
            response = self.supabase.table('messages')\
                .select("*")\
                .eq("user_phone", user_phone)\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching user messages: {e}")
            return []

# Global logger instance
logger = ConversationLogger()

if __name__ == "__main__":
    # Test
    print("🧪 Testing conversation logger with messages table...")
    result = logger.save_conversation(
        room_name="test-room",
        user_message="مرحباً، أريد حجز موعد",
        ai_response="أهلاً بك! سأساعدك في حجز موعد. ما هو اسمك؟",
        language="ar",
        session_id="test-session-001",
        user_phone="+966501234567"
    )
    print(f"✅ Saved conversation turn:")
    print(f"   User message ID: {result['user']['message_id']}")
    print(f"   Assistant message ID: {result['assistant']['message_id']}")

    # Get messages back
    messages = logger.get_messages_by_conversation("test-session-001")
    print(f"\n📋 Retrieved {len(messages)} messages:")
    for msg in messages:
        print(f"   [{msg['role']}]: {msg['content'][:40]}...")
