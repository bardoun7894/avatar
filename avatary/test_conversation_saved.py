#!/usr/bin/env python3
"""
Quick test to check if conversations are being saved
"""
from conversation_logger import ConversationLogger
from datetime import datetime, timedelta

logger = ConversationLogger()

print("\n" + "="*60)
print("Testing Conversation Logging")
print("="*60 + "\n")

# Get recent messages (last hour)
print("Checking for recent conversations...")

try:
    # Try to get recent messages from any room
    response = logger.supabase.table('messages')\
        .select("*")\
        .order('timestamp', desc=True)\
        .limit(10)\
        .execute()

    if response.data:
        print(f"\n✅ Found {len(response.data)} recent messages:\n")
        for msg in response.data:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:50]
            timestamp = msg.get('timestamp', '')
            room = msg.get('room_name', 'unknown')
            print(f"[{timestamp}] {role.upper()} in {room}:")
            print(f"   {content}...")
            print()
    else:
        print("\n⚠️  No messages found in database")
        print("   This could mean:")
        print("   1. No conversations have happened yet")
        print("   2. Messages are not being saved")
        print("   3. Database connection issue")

except Exception as e:
    print(f"\n❌ Error accessing database: {e}")
    import traceback
    traceback.print_exc()

print("="*60 + "\n")
