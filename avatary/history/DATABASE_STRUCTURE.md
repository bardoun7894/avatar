# Database Structure - Supabase

## Tables Overview

### 1. **users** - Customer/Patient Information
Stores user data collected during conversations and appointments.

```sql
- id (SERIAL PRIMARY KEY)
- name (TEXT) - Customer name
- phone (TEXT UNIQUE) - Phone number (unique identifier)
- email (TEXT) - Email address
- created_at (TIMESTAMP) - First time user was added
- updated_at (TIMESTAMP) - Last time user info was updated
- last_interaction (TIMESTAMP) - Last conversation/appointment
```

**Indexes:**
- `idx_users_phone` - Fast lookup by phone
- `idx_users_email` - Fast lookup by email

**Auto-saved when:**
- User books an appointment
- Can be manually updated during conversation

---

### 2. **appointments** - Booking System
Stores all dental appointments.

```sql
- id (TEXT PRIMARY KEY) - Format: APT0001, APT0002, etc.
- patient_name (TEXT) - Full name
- phone (TEXT) - Contact number
- email (TEXT) - Email address
- service (TEXT) - Type of service (تنظيف, فحص, حشوة, etc.)
- date (TEXT) - Appointment date (YYYY-MM-DD)
- time (TEXT) - Appointment time (HH:MM)
- notes (TEXT) - Additional notes
- status (TEXT) - 'confirmed', 'cancelled', etc.
- created_at (TIMESTAMP) - When appointment was booked
```

**Indexes:**
- `idx_appointments_phone` - Find appointments by phone
- `idx_appointments_date` - Find appointments by date
- `idx_appointments_status` - Filter by status

**MCP Tools:**
- `book_appointment` - Create new appointment
- `check_available_slots` - Check availability
- `get_my_appointments` - Get user's appointments
- `cancel_appointment` - Cancel appointment
- `send_confirmation_email` - Send confirmation

---

### 3. **messages** - Conversation History (RECOMMENDED)
Individual message tracking for better conversation management.

```sql
- message_id (UUID PRIMARY KEY) - Unique message identifier
- conversation_id (TEXT) - Groups messages (session or room)
- role (TEXT) - 'user' or 'assistant'
- content (TEXT) - The actual message
- user_phone (TEXT) - Optional link to users table
- room_name (TEXT) - LiveKit room name
- timestamp (TIMESTAMP) - When message was sent
- metadata (JSONB) - Extra data (language, sentiment, etc.)
```

**Indexes:**
- `idx_messages_conversation` - Get all messages in a conversation
- `idx_messages_timestamp` - Order by time
- `idx_messages_user_phone` - Get user's messages
- `idx_messages_room` - Get room messages

**Benefits:**
- Each message is a separate row
- Easy to reconstruct conversations
- Can filter by role (user/assistant)
- Can track individual user message history
- Supports metadata for future features

**Example Queries:**
```sql
-- Get full conversation
SELECT * FROM messages
WHERE conversation_id = 'session-123'
ORDER BY timestamp ASC;

-- Get only user messages
SELECT * FROM messages
WHERE role = 'user' AND conversation_id = 'session-123';

-- Get all messages from a user
SELECT * FROM messages
WHERE user_phone = '+966501234567'
ORDER BY timestamp DESC;

-- Get last 10 messages in a conversation
SELECT * FROM messages
WHERE conversation_id = 'session-123'
ORDER BY timestamp DESC
LIMIT 10;
```

---

## 4. **conversations** (OLD - Keep for backward compatibility)
The original table that stores user+AI response pairs.

```sql
- id (UUID)
- room_name (TEXT)
- user_message (TEXT)
- ai_response (TEXT)
- language (TEXT)
- session_id (TEXT)
- created_at (TIMESTAMP)
```

**Note:** This is being replaced by the `messages` table for better flexibility.

---

## Setup Instructions

### 1. Create users table
```sql
-- See: create_users_table.sql
```

### 2. Create messages table
```sql
-- See: create_messages_table.sql
```

### 3. Appointments table (already created)
Already set up and working.

---

## How Data Flows

### Appointment Booking Flow:
1. User talks to avatar: "أريد حجز موعد"
2. Agent asks for details (name, phone, date, time)
3. `book_appointment` tool is called
4. **Automatically saves to:**
   - `users` table (name, phone, email)
   - `appointments` table (full appointment details)

### Conversation Logging Flow:
1. User says something → Saved to `messages` table (role='user')
2. Agent responds → Saved to `messages` table (role='assistant')
3. Both messages linked by `conversation_id`
4. Optional: `user_phone` links to `users` table

---

## Python Integration

### Files:
- `users_manager.py` - Manages users table
- `conversation_logger.py` - Manages messages table
- `local_mcp_server.py` - Manages appointments + auto-saves users
- `agent.py` - Logs conversations automatically

### Usage in Agent:
```python
# Conversations auto-logged when user talks to avatar
conversation_logger.save_conversation(
    room_name=ctx.room.name,
    user_message="مرحباً",
    ai_response="أهلاً بك!",
    session_id=ctx.room.name,
    user_phone="+966501234567"  # If known
)

# Users auto-saved when booking appointment
users_mgr.save_user(
    name="أحمد محمد",
    phone="+966501234567",
    email="ahmad@example.com"
)
```

---

## Current Status

✅ **appointments** - Working, integrated with MCP tools
✅ **users** - Created, auto-saves on appointment booking
🔄 **messages** - New table, need to run SQL to create
✅ **conversations** - Old table, still exists for compatibility

---

## Next Steps

1. Run `create_users_table.sql` in Supabase SQL Editor
2. Run `create_messages_table.sql` in Supabase SQL Editor
3. Restart agent to use new structure
4. Test conversation logging
5. Later: migrate old conversations to messages table (optional)
