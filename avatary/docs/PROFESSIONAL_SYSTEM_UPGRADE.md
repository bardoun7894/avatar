# Professional Interactive Avatar System - Upgrade Guide

## What's New

### ✅ Professional Conversation Flow

**Old System** (Had Issues):
- ❌ Messages saved directly to database (slow, potential lag)
- ❌ No conversation record, only messages
- ❌ Can't list conversations, only messages
- ❌ Hard to find specific conversation

**New System** (Professional):
- ✅ Messages buffered locally during call (fast, no lag)
- ✅ Conversation record created at start
- ✅ Everything saved to database when call ends
- ✅ Can list all conversations
- ✅ Can view specific conversation with all messages
- ✅ Professional call center experience

---

## Step 1: Create Conversations Table

Run this SQL in Supabase:

```bash
cd /var/www/avatar\ /avatary
# Copy SQL content
cat create_conversations_table.sql
```

Then paste in Supabase SQL Editor and run.

**This creates:**
- `conversations` table with metadata
- Indexes for fast queries
- RLS policies
- Tracking: user info, duration, message count, status

---

## Step 2: Test Professional Manager

```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 professional_conversation_manager.py
```

**Expected Output:**
```
✅ Conversation started: test-xxxxx
📝 Buffered user message locally (1 messages in buffer)
📝 Buffered assistant message locally (2 messages in buffer)
📝 Buffered user message locally (3 messages in buffer)
📝 Buffered assistant message locally (4 messages in buffer)

🏁 Ending conversation: test-xxxxx
   Messages to save: 4
💾 Transcript saved locally: /tmp/transcript_test-xxxxx_20251105_142030.json
✅ Saved 4/4 messages to database
✅ Conversation record updated
   Duration: 1.5s
   User: أحمد محمد
   Phone: +963991234567
```

---

## Step 3: How It Works

### During Call (Fast - No Database):

```python
from professional_conversation_manager import ProfessionalConversationManager

manager = ProfessionalConversationManager()

# 1. Start conversation
manager.start_conversation(
    conversation_id="room-abc123",
    room_name="room-abc123",
    participant_identity="user-456"
)
# → Creates conversation record in database (status: "active")

# 2. User speaks
manager.add_message_to_local_transcript("user", "مرحباً")
# → Saved to LOCAL BUFFER (fast, no lag!)

# 3. Agent responds
manager.add_message_to_local_transcript("assistant", "أهلاً بك...")
# → Saved to LOCAL BUFFER (fast, no lag!)

# ... conversation continues ...
```

### When Call Ends (Save to Database):

```python
# 4. User disconnects
manager.end_conversation(
    user_name="أحمد محمد",
    user_phone="+963991234567",
    summary="استفسار عن التدريبات"
)
# → Saves ALL messages to database
# → Updates conversation record (status: "completed")
# → Saves backup to /tmp/
# → Clears local buffer
```

---

## Step 4: Update agent.py

**Changes needed in agent.py:**

### A. Import the manager (line 24):

```python
from professional_conversation_manager import ProfessionalConversationManager

# Initialize
professional_manager = ProfessionalConversationManager()
```

### B. Start conversation when agent starts (after line 100):

```python
# Create conversation ID
conversation_id = ctx.room.name or f"session-{os.urandom(4).hex()}"

# START CONVERSATION RECORD
professional_manager.start_conversation(
    conversation_id=conversation_id,
    room_name=ctx.room.name,
    participant_identity=ctx.participant.identity if ctx.participant else None,
    metadata={"language": "ar", "avatar_provider": avatar_provider}
)
```

### C. Replace conversation_item_added event (line 283):

```python
# Track user info globally
extracted_user_info = {"name": None, "phone": None, "email": None}

@session.on("conversation_item_added")
def on_conversation_item_added(event: ConversationItemAddedEvent):
    """Buffer messages locally (fast, no database lag)"""
    try:
        global extracted_user_info

        role = event.item.role
        content = event.item.text_content

        if content and content.strip():
            # Save to LOCAL BUFFER (fast!)
            professional_manager.add_message_to_local_transcript(
                role=role,
                content=content,
                metadata={"language": "ar"}
            )

            # Extract user info
            if role == "user":
                user_info = extract_user_info(content)
                if user_info["name"]:
                    extracted_user_info["name"] = user_info["name"]
                if user_info["phone"]:
                    extracted_user_info["phone"] = user_info["phone"]

    except Exception as e:
        print(f"Error buffering message: {e}")
```

### D. Replace shutdown callback (line 302):

```python
async def save_final_conversation():
    """Save complete conversation to database when call ends"""
    try:
        print("\n🏁 Call ended - Saving to database...")

        # Save everything to database
        result = professional_manager.end_conversation(
            user_name=extracted_user_info.get("name"),
            user_phone=extracted_user_info.get("phone"),
            user_email=extracted_user_info.get("email"),
            summary=f"محادثة مع {extracted_user_info.get('name') or 'عميل'}"
        )

        if result:
            print(f"✅ Conversation saved successfully!")
            print(f"   Messages: {result['messages_saved']}")
            print(f"   Duration: {result['duration_seconds']:.1f}s")

            # Save user to users table if we have info
            if extracted_user_info.get("name") and extracted_user_info.get("phone"):
                try:
                    users_manager.save_user(
                        name=extracted_user_info["name"],
                        phone=extracted_user_info["phone"]
                    )
                    print(f"✅ User info saved")
                except Exception as e:
                    print(f"⚠️  Error saving user: {e}")

    except Exception as e:
        print(f"❌ Error saving conversation: {e}")
        import traceback
        traceback.print_exc()

ctx.add_shutdown_callback(save_final_conversation)
```

---

## Step 5: Benefits

### For Users:
- ✅ **No lag** during conversation (messages buffered locally)
- ✅ **Fast response** (no database calls during call)
- ✅ **Professional experience** (smooth interaction)

### For You:
- ✅ **List all conversations** easily
- ✅ **View conversation details** (who, when, how long)
- ✅ **Search by user** phone number
- ✅ **Get statistics** (average duration, message count, etc.)
- ✅ **Backup files** in /tmp/ for safety

### For Frontend:
- ✅ **Conversation list API**:
  ```python
  conversations = manager.get_conversation_list(limit=20)
  # Returns: [
  #   {
  #     "conversation_id": "room-123",
  #     "user_name": "أحمد محمد",
  #     "started_at": "2025-11-05T14:20:00",
  #     "duration_seconds": 180,
  #     "message_count": 12,
  #     "status": "completed"
  #   },
  #   ...
  # ]
  ```

- ✅ **Get specific conversation**:
  ```python
  full = manager.get_conversation_with_messages("room-123")
  # Returns conversation + all messages
  ```

---

## Step 6: Queries You Can Run

### Get all conversations:
```sql
SELECT * FROM conversations ORDER BY started_at DESC LIMIT 10;
```

### Get active conversations:
```sql
SELECT * FROM conversations WHERE status = 'active';
```

### Get user's conversation history:
```sql
SELECT * FROM conversations
WHERE user_phone = '+963991234567'
ORDER BY started_at DESC;
```

### Get conversation statistics:
```sql
SELECT
    status,
    COUNT(*) as count,
    AVG(duration_seconds) as avg_duration,
    AVG(message_count) as avg_messages
FROM conversations
GROUP BY status;
```

### Get today's conversations:
```sql
SELECT * FROM conversations
WHERE DATE(started_at) = CURRENT_DATE
ORDER BY started_at DESC;
```

---

## Summary

**What Changes:**
1. ✅ Create `conversations` table (SQL)
2. ✅ Use `ProfessionalConversationManager` instead of `ConversationLogger`
3. ✅ Buffer messages locally during call (fast)
4. ✅ Save to database when call ends (professional)

**Result:**
- Fast, professional interactive avatar
- Complete conversation tracking
- Easy to list and search conversations
- Backup files for safety
- Ready for production call center! 🎯
