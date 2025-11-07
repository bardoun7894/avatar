# 🎯 ORNINA PHASE 1 - READY TO START

## ✅ What's Been Prepared

Your system is now configured for **Phase 1: Simple Q&A Agent**

### Files Ready:
- ✅ `prompts.py` - Full Ornina company knowledge in Arabic
- ✅ `agent.py` - Updated and simplified
- ✅ `local_mcp_server.py` - Empty (no tools for Phase 1)
- ✅ `conversation_logger.py` - Will save conversations
- ✅ `users_manager.py` - Will save user info

### What Phase 1 Does:
1. **Agent explains Ornina company** in Arabic
2. **Lists all 6 services** when asked
3. **Explains training programs** when asked
4. **Saves conversations** to Supabase
5. **NO booking tools** (added in Phase 2)

---

## 🚀 HOW TO START PHASE 1

### Step 1: Create Database Tables (5 minutes)

Open this file and copy the SQL:
📄 **PHASE1_START_HERE.md**

Or run this SQL in Supabase:

```sql
-- Users table
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

-- Messages table
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

### Step 2: Start the Agent

```bash
pkill -f "python.*agent"

cd "/var/www/avatar /avatary"
source venv/bin/activate
python3 agent.py dev
```

### Step 3: Test Conversation

Try these questions:
- "مرحباً، شو هي شركة أورنينا؟"
- "شو خدماتكم؟"
- "حكيلي عن AI Call Center"
- "في عندكم دورات تدريبية؟"

---

## 📊 Expected Behavior

### ✅ What Should Work:
- Agent speaks Arabic
- Agent explains Ornina company
- Agent lists services:
  1. AI Call Center
  2. Film Production
  3. Smart Advertising
  4. Animation 2D/3D
  5. Website Development
  6. Digital Platform
- Agent lists training programs (6 programs)

### ❌ What Won't Work Yet (Normal):
- NO booking appointments
- NO saving inquiries
- NO scheduling consultations
- These are added in Phase 2-5

---

## 🔍 How to Verify It's Working

### Check 1: Agent Responds
```
You: "مرحباً"
Agent: Should greet and introduce Ornina
```

### Check 2: Services Explained
```
You: "شو خدماتكم؟"
Agent: Should list 6 services
```

### Check 3: Database Saving (OPTIONAL)
- Go to Supabase → Table Editor
- Check `messages` table
- Your conversations should appear there

---

## 📁 File Structure

```
/var/www/avatar /avatary/
├── agent.py                      ← Main agent (ready ✅)
├── prompts.py                    ← Ornina knowledge (ready ✅)
├── local_mcp_server.py          ← Empty for Phase 1 (ready ✅)
├── conversation_logger.py        ← Saves messages (ready ✅)
├── users_manager.py             ← Saves users (ready ✅)
│
├── PHASE1_START_HERE.md         ← Quick start guide
├── PHASED_IMPLEMENTATION.md     ← Full phase plan
├── README_PHASE1.md             ← This file
│
└── Phase 2-5 Files (Not Used Yet):
    ├── local_mcp_server_full.py      ← Full version (for later)
    ├── inquiry_manager.py            ← For Phase 3
    ├── consultation_manager.py       ← For Phase 4
    └── training_manager.py           ← For Phase 5
```

---

## 🎯 Phase 1 Success = Ready for Phase 2

**When Phase 1 works perfectly:**
- ✅ Agent answers questions correctly
- ✅ No errors in logs
- ✅ Conversations saved (optional check)

**Then we add Phase 2:**
- Add simple contact saving tool
- Agent asks for name/phone
- Test that feature
- Move to Phase 3

---

## 🚨 Troubleshooting

**"Could not find table messages"**
→ Run SQL in Supabase first

**"Agent not responding"**
→ Check: `tail -f agent.log`
→ Look for errors

**"Wrong company info"**
→ Check prompts.py has Ornina info

**"Trying to use tools"**
→ Normal - agent might try but tools are disabled

---

## 📞 What Agent Knows (Phase 1)

**Company Info:**
- Name: شركة أورنينا (Ornina)
- Location: دمشق - المزرعة - مقابل وزارة التربية
- Phone: 3349028
- Social: @ornina.official

**Services:**
1. AI Call Center
2. Film & Series Production
3. Smart Advertising
4. Animation 2D/3D
5. Website Development
6. Digital Platform

**Training Programs:**
1. Digital Marketing (45h)
2. Film Production (30h)
3. UI/UX Design (30h)
4. Code Generation (30h)
5. Fashion Design (10h)
6. Website Development (30h)

---

## 🎬 Next Steps

1. **You:** Run SQL in Supabase
2. **You:** Start agent
3. **You:** Test conversation
4. **Me:** Help verify it works
5. **Together:** Move to Phase 2 when ready

---

**Phase 1 is simple on purpose - we test the foundation before building more!** 🚀
