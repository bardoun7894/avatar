# Conversation Transcript System - Complete Guide

## What's Been Fixed

The conversation saving system now uses the correct LiveKit event: `conversation_item_added`

This event fires whenever text input or output is committed to the chat history, allowing us to capture both user messages and agent responses.

---

## How It Works

### 1. Agent Captures Conversations

**Event Handler in agent.py:**
```python
@session._conversation_item_added
def on_conversation_item_added(item):
    # Extract role (user/assistant) and content
    # Save to database
    # Extract user info if present
```

**What Gets Saved:**
- User messages (transcribed from voice)
- Agent responses
- Timestamp
- Conversation ID (room name)
- Metadata (language, etc.)

### 2. Database Storage

**Table: messages**
```sql
message_id      | UUID
conversation_id | TEXT (room name or session ID)
role            | TEXT (user or assistant)
content         | TEXT (the actual message)
user_phone      | TEXT (optional)
room_name       | TEXT
timestamp       | TIMESTAMP
metadata        | JSONB
```

### 3. Frontend API

**Retrieve Transcripts:**
- By conversation_id
- By room_name
- By user_phone
- In multiple formats (JSON, text, HTML)

---

## Usage Guide

### Start Agent with Conversation Logging

```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 agent.py dev
```

**Expected Logs:**
```
Conversation ID: room-xyz-123
حفظ المحادثات مفعّل - Conversation logging ENABLED

[USER]: مرحباً...
تم حفظ رسالة - user message saved!

[ASSISTANT]: أهلاً بك في شركة أورنينا...
تم حفظ رسالة - assistant message saved!
```

### Retrieve Transcripts (Python)

```python
from conversation_logger import ConversationLogger

logger = ConversationLogger()

# Get conversation by ID
messages = logger.get_messages_by_conversation("room-xyz-123")

# Get messages by room
messages = logger.get_messages_by_room("room-xyz-123", limit=50)

# Get user's messages
messages = logger.get_user_messages("+966501234567", limit=20)
```

### Retrieve Transcripts (API)

**Option A: Using get_transcript_api.py directly**
```python
from get_transcript_api import TranscriptAPI

api = TranscriptAPI()

# Get full conversation
result = api.get_conversation_transcript("room-xyz-123")

print(f"Messages: {result['message_count']}")
print(result['transcript_text'])  # Plain text
print(result['transcript_html'])  # HTML formatted
```

**Option B: Flask REST API**
```python
# In get_transcript_api.py, uncomment:
flask_app = create_flask_app()
flask_app.run(host='0.0.0.0', port=5000)
```

**Then access:**
```
GET http://localhost:5000/api/transcript/{conversation_id}
GET http://localhost:5000/api/transcript/room/{room_name}
GET http://localhost:5000/api/transcript/user/{phone}
```

**Option C: FastAPI (Recommended)**
```bash
# Install FastAPI
pip install fastapi uvicorn

# Run server
python3 << 'EOF'
from get_transcript_api import create_fastapi_app
import uvicorn

app = create_fastapi_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

**Then access:**
```
GET http://localhost:8000/api/transcript/{conversation_id}
GET http://localhost:8000/api/transcript/room/{room_name}?limit=100
GET http://localhost:8000/api/transcript/user/{phone}?limit=50
GET http://localhost:8000/docs  # Interactive API docs
```

---

## Transcript Formats

### JSON Format
```json
{
  "conversation_id": "room-xyz-123",
  "message_count": 10,
  "messages": [
    {
      "message_id": "uuid-123",
      "role": "user",
      "content": "مرحباً، شو هي أورنينا؟",
      "timestamp": "2025-11-05T09:00:00",
      "room_name": "room-xyz-123"
    },
    {
      "message_id": "uuid-456",
      "role": "assistant",
      "content": "أهلاً بك! شركة أورنينا هي...",
      "timestamp": "2025-11-05T09:00:02",
      "room_name": "room-xyz-123"
    }
  ]
}
```

### Text Format
```
[2025-11-05T09:00:00] User: مرحباً، شو هي أورنينا؟
[2025-11-05T09:00:02] Agent: أهلاً بك! شركة أورنينا هي...
[2025-11-05T09:00:10] User: شو الخدمات يلي تقدموها؟
[2025-11-05T09:00:12] Agent: لدينا 6 خدمات رئيسية...
```

### HTML Format
```html
<div class="conversation-transcript">
  <div class="message user-message">
    <div class="message-header">
      <span class="role">المستخدم</span>
      <span class="timestamp">2025-11-05T09:00:00</span>
    </div>
    <div class="message-content">مرحباً، شو هي أورنينا؟</div>
  </div>
  <div class="message agent-message">
    <div class="message-header">
      <span class="role">الوكيل</span>
      <span class="timestamp">2025-11-05T09:00:02</span>
    </div>
    <div class="message-content">أهلاً بك! شركة أورنينا هي...</div>
  </div>
</div>
```

---

## Frontend Integration

### React Example
```javascript
// Fetch conversation transcript
async function getTranscript(conversationId) {
  const response = await fetch(
    `http://localhost:8000/api/transcript/${conversationId}`
  );
  const data = await response.json();

  return {
    messages: data.messages,
    html: data.transcript_html,
    text: data.transcript_text
  };
}

// Display in React
function TranscriptView({ conversationId }) {
  const [transcript, setTranscript] = useState(null);

  useEffect(() => {
    getTranscript(conversationId).then(setTranscript);
  }, [conversationId]);

  if (!transcript) return <div>Loading...</div>;

  return (
    <div>
      <h2>Conversation ({transcript.messages.length} messages)</h2>
      {transcript.messages.map(msg => (
        <div key={msg.message_id} className={msg.role}>
          <strong>{msg.role}:</strong> {msg.content}
          <small>{msg.timestamp}</small>
        </div>
      ))}
    </div>
  );
}
```

### Vue Example
```javascript
// Vue component
export default {
  data() {
    return {
      transcript: null,
      conversationId: 'room-xyz-123'
    };
  },
  async mounted() {
    const response = await fetch(
      `http://localhost:8000/api/transcript/${this.conversationId}`
    );
    this.transcript = await response.json();
  },
  template: `
    <div v-if="transcript">
      <h2>Conversation ({{ transcript.message_count }} messages)</h2>
      <div v-for="msg in transcript.messages" :key="msg.message_id"
           :class="msg.role">
        <strong>{{ msg.role }}:</strong> {{ msg.content }}
      </div>
    </div>
  `
};
```

---

## Testing

### Test Conversation Saving
```bash
# 1. Start agent
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 agent.py dev

# 2. Have a conversation
# Say: "مرحباً"
# Agent: "أهلاً بك..."

# 3. Check database
python3 << 'EOF'
from conversation_logger import ConversationLogger

logger = ConversationLogger()
messages = logger.get_messages_by_conversation("room-name")

for msg in messages:
    print(f"[{msg['role']}]: {msg['content']}")
EOF
```

### Test Transcript API
```bash
# Run Flask
python3 get_transcript_api.py

# In another terminal, test
curl http://localhost:5000/api/transcript/test-session-001
```

---

## Troubleshooting

### Issue: Messages not saving
**Check:**
1. Is agent.py using the new version with `conversation_item_added`?
2. Are logs showing "تم حفظ رسالة - message saved!"?
3. Does messages table exist in Supabase?

**Fix:**
```bash
# Verify agent.py
grep "conversation_item_added" agent.py

# Check database
python3 check_supabase_tables.py
```

### Issue: No conversation_id
**Problem:** conversation_id is None
**Fix:** conversation_id defaults to room.name, make sure room is created

### Issue: API returns empty
**Problem:** No messages found
**Cause:** Wrong conversation_id or room_name
**Fix:** Check actual conversation_id in agent logs

---

## Files Created/Modified

| File | Purpose | Status |
|------|---------|--------|
| `agent.py` | Main agent with conversation logging | ✅ FIXED |
| `conversation_logger.py` | Database save/retrieve | ✅ Existing |
| `get_transcript_api.py` | REST API for frontend | ✅ NEW |
| `CONVERSATION_TRANSCRIPT_GUIDE.md` | This guide | ✅ NEW |

---

## Next Steps

### For Production:
1. Add authentication to API endpoints
2. Add pagination for large conversations
3. Add search/filter capabilities
4. Add real-time transcript streaming (WebSocket)
5. Add transcript export (PDF, TXT, JSON)

### For Frontend:
1. Create React/Vue component for transcript display
2. Add real-time updates (poll or WebSocket)
3. Add search within transcripts
4. Add export functionality
5. Add user feedback on transcripts

---

## Summary

**What You Have Now:**
- ✅ All conversations automatically saved to database
- ✅ Both user and agent messages captured
- ✅ Timestamped and organized by conversation_id
- ✅ User info automatically extracted
- ✅ REST API ready for frontend
- ✅ Multiple output formats (JSON, text, HTML)

**Test Now:**
```bash
# Start agent
python3 agent.py dev

# Have conversation
# Say something to the agent

# Check messages saved
python3 -c "from conversation_logger import ConversationLogger; print(ConversationLogger().get_messages_by_room('room-name'))"
```

**Your transcripts are now ready for the frontend! 🎉**
