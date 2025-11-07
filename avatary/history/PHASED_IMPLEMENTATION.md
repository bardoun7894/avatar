# 🎯 ORNINA PHASED IMPLEMENTATION PLAN

## Overview
Transform the system step-by-step to avoid errors and test each phase before moving forward.

---

## ✅ PHASE 1: Basic Agent + Conversation Saving (START HERE)

**Goal:** Agent answers questions about Ornina company and services. Save conversations and user data.

**What Works:**
- ✅ Agent introduces itself as Ornina
- ✅ Explains company services in Arabic
- ✅ Answers questions about what Ornina does
- ✅ Conversations saved to Supabase
- ✅ User names/phones saved when mentioned

**What's NOT Active Yet:**
- ❌ No booking tools
- ❌ No inquiry forms
- ❌ No consultation scheduling
- ❌ Just conversation only

**Database Needed:**
- `users` table
- `messages` table

**SQL to Run (Supabase):**
```sql
-- 1. Users table
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

-- 2. Messages table
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

**Test Conversation:**
```
User: "مرحباً، شو هي شركة أورنينا؟"
Agent: "أهلاً بك! شركة أورنينا هي شركة رائدة في تقديم حلول الذكاء الاصطناعي..."

User: "شو خدماتكم؟"
Agent: "نحن نقدم 6 خدمات رئيسية..."

User: "حكيلي عن AI Call Center"
Agent: "نظام Call Center الذكي من أورنينا..."
```

**Expected Result:**
- Agent answers all questions correctly
- NO tools called
- Just information sharing
- Conversations appear in `messages` table

---

## 🔄 PHASE 2: Add Simple Lead Capture (FUTURE)

**Goal:** Collect customer name and phone when they're interested.

**What Adds:**
- Simple tool: `save_contact`
- Agent asks: "ممكن اسمك ورقم هاتفك؟"
- Saves to `users` table

**Database Adds:**
- `leads` table (simple contact list)

**Not Implemented Yet** - Wait for Phase 1 to work first!

---

## 🚀 PHASE 3: Add Inquiry Saving (FUTURE)

**Goal:** Save what customer is asking about.

**What Adds:**
- Tool: `save_inquiry`
- `inquiries` table
- Track which service interested

**Not Implemented Yet**

---

## 📅 PHASE 4: Add Consultation Booking (FUTURE)

**Goal:** Let customers book appointments.

**What Adds:**
- Tool: `schedule_consultation`
- Tool: `check_available_slots`
- `consultations` table

**Not Implemented Yet**

---

## 🎓 PHASE 5: Add Training Registration (FUTURE)

**Goal:** Let students sign up for training.

**What Adds:**
- Tool: `register_training`
- `training_registrations` table

**Not Implemented Yet**

---

## 📝 CURRENT STATUS: PHASE 1 ONLY

We will implement **PHASE 1 ONLY** right now:
- Simple prompts (already done ✅)
- NO MCP tools
- NO complex booking
- Just Q&A about company
- Save conversations
- Save user info when mentioned

---

## 🎯 PHASE 1 IMPLEMENTATION CHECKLIST

### 1. Supabase Setup
- [ ] Run users table SQL
- [ ] Run messages table SQL
- [ ] Verify tables exist in Supabase

### 2. Code Changes
- [ ] Use simple prompts.py (info only, no tools)
- [ ] Disable all MCP tools for now
- [ ] Keep conversation logger
- [ ] Keep users manager

### 3. Testing
- [ ] Start agent
- [ ] Ask: "شو هي أورنينا؟"
- [ ] Agent explains company
- [ ] Check messages table - conversation saved?
- [ ] Mention name in conversation
- [ ] Check users table - user saved?

### 4. Success Criteria
- ✅ Agent responds in Arabic
- ✅ Explains Ornina services correctly
- ✅ No errors in logs
- ✅ Conversations in database
- ✅ Users in database

---

## 🚨 WHAT TO AVOID IN PHASE 1

❌ Don't use MCP tools yet
❌ Don't try to book appointments
❌ Don't create inquiries/consultations tables yet
❌ Don't test complex scenarios

✅ Just test basic Q&A
✅ Just verify saving works
✅ Keep it simple!

---

## 📋 FILES FOR PHASE 1

**Active Files:**
- `prompts.py` - Ornina info (already updated ✅)
- `agent.py` - Basic agent (already updated ✅)
- `conversation_logger.py` - Save messages
- `users_manager.py` - Save users

**Inactive Files (Don't Use Yet):**
- `local_mcp_server.py` - Tools disabled for Phase 1
- `inquiry_manager.py` - Not used yet
- `consultation_manager.py` - Not used yet
- `training_manager.py` - Not used yet

---

## 🎬 READY FOR PHASE 1?

1. I'll create a simple version without tools
2. You run the 2 SQL scripts above
3. We test basic conversation
4. If works → Move to Phase 2
5. If errors → Fix before continuing

**This way we test each piece before adding complexity!**
