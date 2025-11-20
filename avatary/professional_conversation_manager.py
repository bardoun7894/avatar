#!/usr/bin/env python3
"""
Professional Conversation Manager
- Saves transcript locally during call (fast, no lag)
- Creates conversation record when call starts
- Saves everything to database when call ends
- Professional interactive avatar system
"""
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class ProfessionalConversationManager:
    """Manages conversations professionally with local buffering"""

    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Local buffer for current conversation
        self.current_conversation_id: Optional[str] = None
        self.local_transcript: List[Dict] = []
        self.conversation_metadata: Dict = {}

    def start_conversation(
        self,
        conversation_id: str,
        room_name: str,
        participant_identity: str = None,
        metadata: dict = None
    ) -> dict:
        """Start a new conversation - creates conversation record in database"""
        try:
            self.current_conversation_id = conversation_id
            self.local_transcript = []
            self.conversation_metadata = {
                "room_name": room_name,
                "participant_identity": participant_identity,
                "started_at": datetime.now().isoformat(),
                **(metadata or {})
            }

            # Check if conversation already exists
            existing = self.supabase.table('conversations')\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .execute()

            if existing.data and len(existing.data) > 0:
                print(f"♻️  Conversation already exists: {conversation_id}")
                print(f"   Room: {room_name}")
                print(f"   Status: {existing.data[0].get('status', 'unknown')}")
                return existing.data[0]

            # Create conversation record in database
            conversation = {
                "conversation_id": conversation_id,
                "room_name": room_name,
                "participant_identity": participant_identity,
                "started_at": self.conversation_metadata["started_at"],
                "status": "active",
                "language": "ar",
                "metadata": metadata or {}
            }

            response = self.supabase.table('conversations').insert(conversation).execute()

            print(f"✅ Conversation started: {conversation_id}")
            print(f"   Room: {room_name}")
            print(f"   Started: {self.conversation_metadata['started_at']}")

            return response.data[0] if response.data else conversation

        except Exception as e:
            print(f"⚠️  Error starting conversation: {e}")
            # Continue anyway with local transcript
            return None

    def add_message_to_local_transcript(
        self,
        role: str,
        content: str,
        metadata: dict = None
    ):
        """Add message to local transcript (fast, no database call)"""
        if not content or not content.strip():
            return

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.local_transcript.append(message)
        print(f"📝 Buffered {role} message locally ({len(self.local_transcript)} messages in buffer)")

    def save_local_transcript_to_file(self) -> str:
        """Save current transcript to local file"""
        try:
            if not self.current_conversation_id:
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/transcript_{self.current_conversation_id}_{timestamp}.json"

            data = {
                "conversation_id": self.current_conversation_id,
                "metadata": self.conversation_metadata,
                "messages": self.local_transcript,
                "message_count": len(self.local_transcript)
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"💾 Transcript saved locally: {filename}")
            return filename

        except Exception as e:
            print(f"⚠️  Error saving local transcript: {e}")
            return None

    def end_conversation(
        self,
        user_name: str = None,
        user_phone: str = None,
        user_email: str = None,
        summary: str = None
    ) -> dict:
        """End conversation and save everything to database"""
        try:
            if not self.current_conversation_id:
                print("⚠️  No active conversation to end")
                return None

            conversation_id = self.current_conversation_id
            ended_at = datetime.now().isoformat()

            print(f"\n🏁 Ending conversation: {conversation_id}")
            print(f"   Messages to save: {len(self.local_transcript)}")

            # 1. Save local transcript to file (backup)
            self.save_local_transcript_to_file()

            # 2. Save all messages to database
            saved_count = 0
            for msg in self.local_transcript:
                try:
                    message_record = {
                        "message_id": str(uuid.uuid4()),
                        "conversation_id": conversation_id,
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg["timestamp"],
                        "room_name": self.conversation_metadata.get("room_name"),
                        "user_phone": user_phone,
                        "metadata": msg.get("metadata", {})
                    }

                    self.supabase.table('messages').insert(message_record).execute()
                    saved_count += 1

                except Exception as e:
                    print(f"⚠️  Error saving message: {e}")

            print(f"✅ Saved {saved_count}/{len(self.local_transcript)} messages to database")

            # 3. Update conversation record
            duration_seconds = None
            if self.conversation_metadata.get("started_at"):
                try:
                    started = datetime.fromisoformat(self.conversation_metadata["started_at"])
                    ended = datetime.fromisoformat(ended_at)
                    duration_seconds = (ended - started).total_seconds()
                except:
                    pass

            conversation_update = {
                "status": "completed",
                "ended_at": ended_at,
                "duration_seconds": duration_seconds,
                "message_count": len(self.local_transcript),
                "user_name": user_name,
                "user_phone": user_phone,
                "user_email": user_email,
                "summary": summary or f"محادثة مع {user_name or 'عميل'}" if user_name else "محادثة مع عميل",
                "updated_at": ended_at
            }

            response = self.supabase.table('conversations')\
                .update(conversation_update)\
                .eq("conversation_id", conversation_id)\
                .execute()

            print(f"✅ Conversation record updated")
            print(f"   Duration: {duration_seconds:.1f}s" if duration_seconds else "")
            print(f"   User: {user_name or 'N/A'}")
            print(f"   Phone: {user_phone or 'N/A'}")

            # 4. Clear local buffer
            result = {
                "conversation_id": conversation_id,
                "messages_saved": saved_count,
                "duration_seconds": duration_seconds,
                "user_info": {
                    "name": user_name,
                    "phone": user_phone,
                    "email": user_email
                }
            }

            self.current_conversation_id = None
            self.local_transcript = []
            self.conversation_metadata = {}

            return result

        except Exception as e:
            print(f"❌ Error ending conversation: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_conversation_list(self, limit: int = 20) -> List[Dict]:
        """Get list of conversations"""
        try:
            response = self.supabase.table('conversations')\
                .select("*")\
                .order("started_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching conversations: {e}")
            return []

    def get_conversation_with_messages(self, conversation_id: str) -> Dict:
        """Get conversation record with all its messages"""
        try:
            # Get conversation
            conv_response = self.supabase.table('conversations')\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .execute()

            if not conv_response.data:
                return None

            conversation = conv_response.data[0]

            # Get messages
            msg_response = self.supabase.table('messages')\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("timestamp", desc=False)\
                .execute()

            conversation["messages"] = msg_response.data if msg_response.data else []

            return conversation

        except Exception as e:
            print(f"⚠️  Error fetching conversation: {e}")
            return None


if __name__ == "__main__":
    # Test the professional system
    print("🧪 Testing Professional Conversation Manager...\n")

    manager = ProfessionalConversationManager()

    # 1. Start conversation
    conv_id = f"test-{uuid.uuid4().hex[:8]}"
    manager.start_conversation(
        conversation_id=conv_id,
        room_name="test-room-123",
        participant_identity="user-456",
        metadata={"source": "web", "language": "ar"}
    )

    # 2. Add messages to local buffer (during call)
    import time
    manager.add_message_to_local_transcript("user", "مرحباً، أريد معلومات عن خدماتكم")
    time.sleep(0.5)
    manager.add_message_to_local_transcript("assistant", "أهلاً بك في شركة أورنينا! نقدم 6 خدمات رئيسية...")
    time.sleep(0.5)
    manager.add_message_to_local_transcript("user", "أنا مهتم بتدريبات الذكاء الاصطناعي")
    time.sleep(0.5)
    manager.add_message_to_local_transcript("assistant", "ممتاز! عندنا 6 تدريبات متخصصة...")

    # 3. End conversation (saves to database)
    print("\n")
    result = manager.end_conversation(
        user_name="أحمد محمد",
        user_phone="+963991234567",
        summary="استفسار عن التدريبات"
    )

    print(f"\n✅ Test completed!")
    print(f"   Conversation ID: {result['conversation_id']}")
    print(f"   Messages saved: {result['messages_saved']}")
    print(f"   Duration: {result['duration_seconds']:.1f}s")

    # 4. Retrieve conversation
    print("\n📋 Retrieving conversation...")
    full_conv = manager.get_conversation_with_messages(conv_id)
    if full_conv:
        print(f"   Status: {full_conv['status']}")
        print(f"   Messages: {len(full_conv['messages'])}")
        for msg in full_conv['messages']:
            print(f"      [{msg['role']}]: {msg['content'][:50]}...")
