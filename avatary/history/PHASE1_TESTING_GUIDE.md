# 🧪 Phase 1 Testing Guide - Ornina Voice Agent

## ✅ What's Been Fixed

### 1. Conversation Saving ✅
- Added event handlers to capture **every user message**
- Added event handlers to capture **every agent response**
- All messages saved to `messages` table with:
  - conversation_id (room name)
  - role (user/assistant)
  - content (the message)
  - timestamp
  - metadata (language: ar)

### 2. User Extraction ✅
- Automatically detects **names and phone numbers** in conversations
- Saves users to `users` table when both name AND phone detected
- Supports patterns like:
  - "اسمي أحمد" (my name is Ahmad)
  - "أنا محمد" (I am Mohammed)
  - Phone formats: +966501234567, 0675 24 70, etc.

### 3. Old Dental Data
- Created cleanup script: `cleanup_old_appointments.py`
- 2 old dental appointments in database
- Can delete, archive, or keep for reference

---

## 🚀 How to Test

### Step 1: Start the Agent

```bash
cd /var/www/avatar\ /avatary
python3 agent.py dev
```

**Expected output:**
```
============================================================
🚀 اتصال جديد! - NEW CONNECTION!
============================================================

🎯 Avatar Mode: AUDIO
🎯 اللغة: العربية - Language: Arabic
🎤 الصوت: أبو سالم (ذكر كويتي) - Voice: Abu Salem (Male, Kuwaiti)
🔧 MCP Server: Local (0 tools for Phase 1)

💾 حفظ المحادثات مفعّل - Conversation logging: ENABLED
   📝 Conversation ID: [room-name]
   💬 All messages will be saved to Supabase messages table

✅ الوكيل جاهز! - AGENT READY!
```

### Step 2: Test Basic Q&A

**Test conversations:**

1. **Company information:**
   ```
   You: "مرحباً، شو هي شركة أورنينا؟"
   Agent: Should explain Ornina is an AI services company in Damascus
   ```

2. **Services:**
   ```
   You: "شو الخدمات اللي تقدموها؟"
   Agent: Should list 6 services (Call Center AI, Film Production, etc.)
   ```

3. **Training programs:**
   ```
   You: "عندكم تدريبات؟"
   Agent: Should list 6 training programs with details
   ```

4. **Contact info:**
   ```
   You: "كيف بقدر تواصل معكم؟"
   Agent: Should provide phone (3349028), address (Al-Mazraa), social media
   ```

### Step 3: Test User Extraction

**Conversation with name and phone:**

```
You: "اسمي أحمد ورقمي 0501234567"
```

**Expected logs:**
```
💾 حفظ رسالة المستخدم - Saving user message...
✅ تم حفظ رسالة المستخدم - User message saved!
👤 اكتشاف معلومات المستخدم - Detected user info: أحمد - 0501234567
✅ Created new user: أحمد (0501234567)
✅ تم حفظ المستخدم - User saved to database!
```

**More examples to test:**
- "أنا محمد، رقمي +966501234567"
- "اسمي فاطمة ورقم تلفوني 3349028"

### Step 4: Verify Data in Supabase

#### Option A: Using Python Script

```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 check_supabase_tables.py
```

**Look for:**
- Messages in `messages` table with your conversation
- Users in `users` table with extracted names/phones

#### Option B: Supabase Dashboard

1. Go to https://supabase.com
2. Open your project: uzzejiaxyvuhcfcvjyiv
3. Go to **Table Editor**
4. Check **messages** table → should see all user/agent messages
5. Check **users** table → should see extracted users

---

## 🔍 Expected Results

### Messages Table
```
message_id                           | conversation_id | role      | content                    | timestamp
-------------------------------------|-----------------|-----------|----------------------------|-------------------
3f5feade-f881-4d0b-8da6-92b75f2c46a7 | room-xyz        | user      | مرحباً، شو هي أورنينا؟    | 2025-11-05 07:30:00
34016f91-d3b4-4df8-903a-9b46b74b32c5 | room-xyz        | assistant | أهلاً بك! شركة أورنينا...  | 2025-11-05 07:30:02
```

### Users Table
```
id | name  | phone        | created_at          | last_interaction
---|-------|--------------|---------------------|------------------
1  | أحمد  | 0501234567   | 2025-11-05 07:35:00 | 2025-11-05 07:35:00
2  | محمد  | +966501234567| 2025-11-05 07:40:00 | 2025-11-05 07:40:00
```

---

## 📊 Cleanup Old Appointments (Optional)

```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 cleanup_old_appointments.py
```

**Options:**
1. Delete all (removes 2 dental appointments)
2. Keep for reference (do nothing)
3. Archive to backup file + optionally delete

**Recommendation:** Archive to backup file, then delete from database to keep it clean.

---

## ✅ Success Criteria

- [x] Agent starts without errors
- [ ] Agent responds in Arabic voice (Abu Salem - Kuwaiti male)
- [ ] Agent correctly answers questions about Ornina
- [ ] All user messages saved to `messages` table
- [ ] All agent responses saved to `messages` table
- [ ] User info extracted when name + phone mentioned
- [ ] Users saved to `users` table

---

## 🐛 Troubleshooting

### No messages being saved
- Check logs for: "✅ تم حفظ رسالة المستخدم - User message saved!"
- If missing, check Supabase credentials in `.env`
- Verify `messages` table exists in Supabase

### No users being saved
- Check logs for: "👤 اكتشاف معلومات المستخدم"
- User extraction requires BOTH name AND phone in same message
- Try format: "اسمي [name] ورقمي [phone]"

### Agent not responding
- Check if ElevenLabs API key is valid
- Check if OpenAI API key is valid
- Check agent.log for errors

### Supabase connection errors
- Verify SUPABASE_URL in .env
- Verify SUPABASE_ANON_KEY in .env
- Check network connection

---

## 📝 What's NOT in Phase 1

These will come in later phases:

- ❌ Lead capture tool (Phase 2)
- ❌ Inquiry saving (Phase 3)
- ❌ Consultation booking (Phase 4)
- ❌ Training registration (Phase 5)

For now, it's **pure Q&A** with conversation and user tracking!

---

## 🎯 Next Steps After Testing

Once Phase 1 is working:

1. ✅ Confirm messages are being saved
2. ✅ Confirm users are being extracted and saved
3. 📊 Review PHASED_IMPLEMENTATION.md for Phase 2
4. 🚀 We'll add simple lead capture tool in Phase 2

---

## 📞 Quick Test Checklist

```
[ ] Agent starts successfully
[ ] Arabic voice works (Abu Salem)
[ ] Agent explains Ornina company
[ ] Agent lists 6 services correctly
[ ] Agent lists 6 training programs correctly
[ ] Agent provides contact info (phone: 3349028, Damascus location)
[ ] Messages appear in Supabase messages table
[ ] Users appear in Supabase users table after giving name+phone
[ ] Old appointments cleaned up (optional)
```

**Test now and report results!** 🚀
