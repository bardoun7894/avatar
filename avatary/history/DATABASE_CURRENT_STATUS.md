# 📊 Database Current Status - Ornina

## ✅ Tables Currently in Supabase (Existing)

### 1. **appointments** (Old Dental Clinic Data)
```
Rows: 2 dental appointments
Columns: id, patient_name, phone, email, service, date, time, notes, status, created_at
Status: ⚠️ OLD DATA - should be cleaned up or archived
```

**Sample data:**
- APT0001: أحمد محمد - تنظيف - 2025-11-10
- APT0002: أبيدر - تنظيف الأسنان - 2023-11-01

**Next action:** Run `cleanup_old_appointments.py` to delete or archive

---

### 2. **agents** (Empty)
```
Rows: 0
Status: 🤔 Purpose unclear - possibly for multi-agent systems
```

---

### 3. **users** (Empty, Ready for Use)
```
Rows: 0
Columns: id, name, phone, email, created_at, updated_at, last_interaction
Status: ✅ READY - will auto-populate when users give name+phone
```

**Auto-populated by:** `agent.py` when user says "اسمي أحمد ورقمي 0501234567"

---

### 4. **messages** (2 test messages)
```
Rows: 2 test messages
Columns: message_id, conversation_id, role, content, user_phone, room_name, timestamp, metadata
Status: ✅ WORKING - saves all conversations now
```

**Sample data:**
- User: "مرحباً، أريد حجز موعد"
- Assistant: "أهلاً بك! سأساعدك في حجز موعد..."

**Auto-populated by:** `agent.py` event handlers (user_speech_committed, agent_speech_committed)

---

### 5. **conversations** (Empty, Old Format)
```
Rows: 0
Status: ⚠️ OLD TABLE - replaced by messages table
```

**Can be deleted:** Not used anymore, kept for backward compatibility

---

## 📝 Tables Planned but NOT Created Yet

These are in `create_ornina_tables.sql` but not run yet:

### 1. **inquiries** (For Phase 3+)
```sql
Purpose: Customer service inquiries, lead capture
Columns: inquiry_id, customer_name, phone, email, company_name,
         service_interest, inquiry_type, message, budget_range,
         timeline, status, assigned_to, notes
Will be used in: Phase 3 (Inquiry Saving)
```

---

### 2. **consultations** (For Phase 4+)
```sql
Purpose: Scheduled consultation meetings
Columns: consultation_id (CON0001), customer_name, phone, email,
         service_type, consultation_date, consultation_time,
         meeting_type (online/in-person), status
Will be used in: Phase 4 (Consultation Booking)
```

---

### 3. **training_registrations** (For Phase 5+)
```sql
Purpose: Training program sign-ups
Columns: registration_id (TRN0001), student_name, phone, email,
         program_name, preferred_start_date, experience_level,
         payment_status, registration_status
Will be used in: Phase 5 (Training Registration)
```

---

## 🆕 FAQ Table (Proposed - Not Created Yet)

### **faqs** (Dynamic Q&A System)
```sql
Purpose: Store questions/answers that aren't in prompts.py
Columns: id, question, answer, category, keywords[], language,
         is_active, view_count, created_at
Benefits:
  - Add Q&A without changing code
  - Update answers in real-time
  - Track popular questions
  - Search by keywords
```

**Example data (ready to insert):**
1. "ما هي أسعار خدماتكم؟" → Answer about pricing
2. "كم مدة التدريبات؟" → Training durations
3. "هل التدريبات أونلاين أم حضوري؟" → Both options
4. "هل تقدمون خدمات خارج سوريا؟" → Yes, international
5. "كيف أبدأ مشروعي معكم؟" → Contact info

---

## 🎯 Recommendations

### Immediate Actions:

1. **Clean up old dental data:**
   ```bash
   cd /var/www/avatar\ /avatary
   source venv/bin/activate
   python3 cleanup_old_appointments.py
   ```
   → Choose option 3: Archive + Delete

2. **Create FAQ table NOW:**
   ```sql
   Run: create_faq_table.sql in Supabase SQL Editor
   ```
   → This is Phase 1.5 - adds dynamic Q&A immediately

3. **Test current Phase 1 features:**
   - Message saving ✅
   - User extraction ✅
   - FAQ search (after creating table)

### Later (Phase 2-5):

4. **Create Ornina tables when ready:**
   ```sql
   Run: create_ornina_tables.sql in Supabase SQL Editor
   ```
   → This creates inquiries, consultations, training_registrations

5. **Delete old tables:**
   ```sql
   DROP TABLE IF EXISTS conversations;  -- After confirming messages works
   DROP TABLE IF EXISTS appointments;    -- After archive
   DROP TABLE IF EXISTS agents;          -- If not needed
   ```

---

## 📊 Summary Table

| Table Name | Status | Rows | Phase | Action Needed |
|------------|--------|------|-------|---------------|
| appointments | ⚠️ Old | 2 | - | Archive & Delete |
| agents | ❓ Unknown | 0 | - | Research purpose or delete |
| users | ✅ Ready | 0 | 1 | No action (auto-fills) |
| messages | ✅ Working | 2 | 1 | No action (auto-fills) |
| conversations | ⚠️ Old | 0 | - | Can delete |
| **faqs** | 🆕 Planned | - | 1.5 | **CREATE NOW** |
| inquiries | 📝 Planned | - | 3 | Create in Phase 3 |
| consultations | 📝 Planned | - | 4 | Create in Phase 4 |
| training_registrations | 📝 Planned | - | 5 | Create in Phase 5 |

---

## 🚀 Next Steps Decision

**Question for you:**

1. **Should I create the FAQ table now?**
   - ✅ Benefit: Agent can search database for answers
   - ✅ Benefit: You can add Q&A without changing code
   - ⚠️ Note: Need to add search tool to agent

2. **Should I create the Ornina tables (inquiries, consultations, training) now?**
   - ✅ Benefit: Database ready for Phase 2-5
   - ⚠️ Note: Won't be used until we add tools in later phases

3. **Should I clean up old tables (appointments, conversations, agents)?**
   - ✅ Benefit: Cleaner database
   - ⚠️ Note: Should archive first

**What would you like to do?**
