# Testing Conversation Logging Fix

## What Was Fixed

### Issue 1: TypeError in on_data_received
**Error**: `TypeError: entrypoint.<locals>.on_data_received() missing 1 required positional argument: 'participant'`

**Cause**: The `on_data_received` event handler had incorrect signature

**Fix**: Removed the buggy handler completely (it wasn't working anyway)

### Issue 2: Chat Context Monitoring Not Working
**Problem**: Messages weren't being captured from the chat context

**Fix**: Improved monitoring to access session internals more deeply:
- Now checks `session._agent_playout._fnc_ctx.chat_ctx.messages`
- Polls twice per second (every 0.5s)
- Added debug print when capturing messages

---

## How to Test

### Step 1: Start the Agent
```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 agent.py dev
```

**Expected Output**:
- No more TypeError errors
- Should see: `📊 Chat monitoring task started`
- Should see: `الوكيل جاهز! - AGENT READY!`

### Step 2: Have a Conversation
Connect to the agent and say:
- "مرحباً"
- "شو خدماتكم؟"
- "شكراً"

**Watch for These Logs**:
```
💾 Capturing user message...
[USER]: مرحباً
تم حفظ رسالة - user message saved!

💾 Capturing assistant message...
[ASSISTANT]: أهلاً بك في شركة أورنينا...
تم حفظ رسالة - assistant message saved!
```

### Step 3: Verify Messages Saved
After the conversation, run:
```bash
python3 test_conversation_saved.py
```

**Expected Output**:
```
✅ Found X recent messages:

[2025-11-05T...] USER in room-xxx:
   مرحباً...

[2025-11-05T...] ASSISTANT in room-xxx:
   أهلاً بك في شركة أورنينا...
```

---

## If It Still Doesn't Work

### Scenario A: No TypeError but still no messages saved

This means the chat context monitoring approach isn't accessing the right internal structure.

**Next Steps**:
1. We'll need to try a different approach
2. Options:
   - Hook into the LLM's chat completion method directly
   - Use LiveKit's built-in transcription events
   - Create a custom Agent class that overrides message handling

### Scenario B: Different errors appear

Share the error logs and we'll debug from there.

### Scenario C: Messages saved but incomplete

If only user OR assistant messages are saved (not both):
- We'll need to add separate handlers for each
- May need to hook into different parts of the framework

---

## Alternative: Use agent_with_logging.py

If the main agent.py still doesn't work, try this version which uses a different approach:

```bash
# Backup current agent
cp agent.py agent_backup.py

# Copy the alternative version
cp agent_with_logging.py agent.py

# Test
python3 agent.py dev
```

---

## Database Quick Check

To manually check what's in the database:
```bash
python3 << 'EOF'
from conversation_logger import ConversationLogger
logger = ConversationLogger()

# Get all messages
messages = logger.supabase.table('messages').select("*").limit(5).execute()
print(f"Total messages: {len(messages.data)}")
for msg in messages.data:
    print(f"{msg['role']}: {msg['content'][:50]}...")
EOF
```

---

## Current Status

✅ **Fixed**:
- TypeError in on_data_received removed
- Improved chat context monitoring
- Added debug logging

⏳ **Needs Testing**:
- Whether messages are now being captured
- Whether both user and assistant messages are saved
- Whether user info extraction still works

---

## Next Steps After Testing

If this works:
- Update prompts to use knowledge base search
- Run the SQL file to populate knowledge base
- Test agent can answer questions from database

If this doesn't work:
- Try alternative approaches
- Consider using LiveKit's built-in event system differently
- May need to patch the Agent class directly
