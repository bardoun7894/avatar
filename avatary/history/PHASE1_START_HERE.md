# 🚀 PHASE 1 - START HERE

## What We're Doing in Phase 1

**Simple Goal:**
- Agent talks about Ornina company
- Agent explains services
- Conversations get saved to database
- User info gets saved when mentioned

**NO booking, NO tools, NO complexity - Just Q&A!**

---

## Step 1: Run SQL in Supabase (2 minutes)

Go to: **https://supabase.com/dashboard** → Your Project → SQL Editor

**Copy and paste this SQL:**

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all access for users" ON users FOR ALL USING (true) WITH CHECK (true);
GRANT ALL ON users TO anon;
GRANT ALL ON users TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO authenticated;

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    user_phone TEXT,
    room_name TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all access for messages" ON messages FOR ALL USING (true) WITH CHECK (true);
GRANT ALL ON messages TO anon;
GRANT ALL ON messages TO authenticated;
```

Click **Run** button.

---

## Step 2: Disable MCP Tools Temporarily

I'll create a simple version of local_mcp_server.py that returns empty tools.

```bash
cd "/var/www/avatar /avatary"
```

---

## Step 3: Start Agent

```bash
# Kill old agent
pkill -f "python.*agent"

# Start Phase 1 agent
cd "/var/www/avatar /avatary"
source venv/bin/activate
python3 agent.py dev
```

---

## Step 4: Test Conversation

Connect to playground and try:

### Test 1: Company Info
```
You: "مرحباً، شو هي شركة أورنينا؟"
Agent: Should explain Ornina company
```

### Test 2: Services
```
You: "شو خدماتكم؟"
Agent: Should list 6 services
```

### Test 3: Specific Service
```
You: "حكيلي عن AI Call Center"
Agent: Should explain Call Center service
```

### Test 4: Training
```
You: "في عندكم دورات تدريبية؟"
Agent: Should list training programs
```

---

## Step 5: Check Database

Go to Supabase → Table Editor → `messages` table

You should see your conversation saved!

---

## ✅ Phase 1 Success Criteria

- [ ] Agent starts without errors
- [ ] Agent speaks Arabic
- [ ] Agent explains Ornina company correctly
- [ ] Agent lists services correctly
- [ ] Conversations appear in `messages` table

---

## 🚨 If You See Errors

**Error: "Could not find table messages"**
→ Run the SQL script above in Supabase

**Error: "Tool not found"**
→ That's OK for Phase 1, we disabled tools

**Error: Agent not responding**
→ Check agent.log file
→ Look for error messages

---

## 📝 What Happens Next?

**If Phase 1 works:**
- ✅ Move to Phase 2 (simple lead capture)
- ✅ Add one tool at a time
- ✅ Test each addition

**If Phase 1 has errors:**
- ❌ Fix errors first
- ❌ Don't add more complexity
- ❌ Debug step by step

---

## 💡 Tips

1. **Keep it simple** - Don't test complex scenarios yet
2. **Check logs** - Look at agent.log for any errors
3. **One thing at a time** - Test each feature separately
4. **Database first** - Make sure tables exist before testing

---

**Let me know when you've:**
1. ✅ Run the SQL
2. ✅ Started the agent
3. ✅ Tested a conversation

Then I'll help you verify everything is working before Phase 2!
