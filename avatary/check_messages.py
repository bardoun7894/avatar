#!/usr/bin/env python3
"""
Check Messages in Database
Verify that messages are being saved correctly
"""
from conversation_logger import ConversationLogger
from professional_conversation_manager import ProfessionalConversationManager
from dotenv import load_dotenv

load_dotenv()

def check_messages():
    print("\n" + "="*80)
    print("📊 DATABASE MESSAGE CHECK")
    print("="*80 + "\n")

    # Initialize managers
    logger = ConversationLogger()
    prof_manager = ProfessionalConversationManager()

    # Check conversations table
    print("🔍 Checking 'conversations' table...")
    conversations = []
    try:
        from supabase import create_client
        import os

        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

        response = supabase.table('conversations')\
            .select("*")\
            .order("started_at", desc=True)\
            .limit(5)\
            .execute()

        conversations = response.data if response.data else []
        print(f"   Found {len(conversations)} recent conversations\n")

        if conversations:
            for i, conv in enumerate(conversations, 1):
                print(f"{i}. Conversation: {conv.get('conversation_id', 'N/A')}")
                print(f"   Room: {conv.get('room_name', 'N/A')}")
                print(f"   Participant: {conv.get('participant_identity', 'N/A')}")
                print(f"   Start: {conv.get('started_at', 'N/A')}")
                print(f"   End: {conv.get('ended_at', 'N/A')}")
                print(f"   Status: {conv.get('status', 'N/A')}")
                print()
        else:
            print("   ⚠️  No conversations found!\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

    # Check messages table
    print("\n" + "-"*80)
    print("🔍 Checking 'messages' table...")
    print("-"*80 + "\n")

    # Try to get messages from the most recent conversation
    if conversations:
        latest_conv_id = conversations[0].get('conversation_id')
        print(f"   Getting messages for conversation: {latest_conv_id}\n")

        try:
            messages = logger.get_messages_by_conversation(latest_conv_id, limit=20)
            print(f"   Found {len(messages)} messages\n")

            if messages:
                for i, msg in enumerate(messages, 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    timestamp = msg.get('timestamp', 'N/A')

                    # Truncate long messages
                    display_content = content[:80] + "..." if len(content) > 80 else content

                    print(f"{i}. [{role.upper()}] at {timestamp}")
                    print(f"   {display_content}")
                    print()
            else:
                print("   ⚠️  No messages found for this conversation!\n")
        except Exception as e:
            print(f"   ❌ Error getting messages: {e}\n")
    else:
        # Try to get any recent messages
        print("   Trying to get any recent messages...\n")
        from supabase import create_client
        import os

        try:
            supabase = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )

            response = supabase.table('messages')\
                .select("*")\
                .order("timestamp", desc=True)\
                .limit(10)\
                .execute()

            messages = response.data if response.data else []
            print(f"   Found {len(messages)} recent messages (across all conversations)\n")

            if messages:
                for i, msg in enumerate(messages, 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    conv_id = msg.get('conversation_id', 'N/A')
                    timestamp = msg.get('timestamp', 'N/A')

                    display_content = content[:60] + "..." if len(content) > 60 else content

                    print(f"{i}. [{role.upper()}] - Conv: {conv_id[:20]}...")
                    print(f"   {display_content}")
                    print(f"   Time: {timestamp}")
                    print()
            else:
                print("   ⚠️  No messages found in database at all!\n")
                print("   This could mean:")
                print("   1. Messages table doesn't exist")
                print("   2. No conversations have happened yet")
                print("   3. Supabase connection issue")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("✅ Check complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    check_messages()
