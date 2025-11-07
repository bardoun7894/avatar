# 🔍 Phase 1.5: Knowledge Base Search - Complete Guide

## 🎉 What's New

**Phase 1.5 adds dynamic database search!**

The agent can now:
- ✅ Search FAQs when user asks questions
- ✅ Look up products/services details
- ✅ Find training program information
- ✅ Query company contact info
- ✅ **Get answers from database, not just prompts.py**

---

## 🆚 Phase 1 vs Phase 1.5

### Phase 1 (Before):
```
User: "ما هي أسعار خدماتكم؟"
Agent: [Uses only prompts.py knowledge]
Agent: "أسعار خدماتنا تختلف حسب المشروع..."
```

### Phase 1.5 (Now):
```
User: "ما هي أسعار خدماتكم؟"
Agent: [Searches database using search_knowledge_base]
Agent: [Finds FAQ with pricing answer]
Agent: "أسعار خدماتنا تختلف حسب نوع المشروع ومتطلباته.
       يرجى التواصل معنا على الرقم 3349028 أو زيارتنا في
       مكتبنا في المزرعة مقابل وزارة التربية للحصول على
       عرض سعر مخصص لمشروعك."
```

---

## 🔧 What Was Added

### 1. New File: `knowledge_base_manager.py`
**Purpose:** Handles all database searches

**Functions:**
- `search_faqs(query)` - Search FAQ table
- `search_products(query)` - Search products table
- `search_training_programs(query)` - Search training table
- `search_services(query)` - Search work_areas table
- `get_company_info(key)` - Get company information
- `smart_search(query)` - Search across all tables

### 2. Updated: `local_mcp_server.py`
**Changed from:** Empty (no tools)
**Changed to:** 4 knowledge base search tools

**New Tools:**
1. `search_knowledge_base` - Smart search across all tables
2. `get_all_products` - List all 6 products/services
3. `get_all_training_programs` - List all 6 training programs
4. `get_company_contact` - Get contact info

### 3. Updated: `prompts.py`
**Added:** Instructions on when/how to use knowledge base search

---

## 📊 Available Tools Explained

### Tool 1: search_knowledge_base
**When to use:**
- User asks specific question you don't know
- Need detailed product information
- Want to find relevant FAQ

**Example:**
```
User: "كم مدة دورة التسويق الرقمي؟"
Agent calls: search_knowledge_base(query="التسويق الرقمي مدة")
Result: Training program with 45 hours duration
Agent: "دورة التسويق الرقمي مدتها 45 ساعة..."
```

### Tool 2: get_all_products
**When to use:**
- User asks: "شو الخدمات يلي عندكم؟"
- User asks: "ماذا تقدمون؟"
- Need to list all services

**Example:**
```
User: "ماذا تقدمون من خدمات؟"
Agent calls: get_all_products()
Result: List of 6 products
Agent: "لدينا 6 خدمات رئيسية:
       1. Call Center بالذكاء الاصطناعي
       2. إنتاج الأفلام والمسلسلات
       ..."
```

### Tool 3: get_all_training_programs
**When to use:**
- User asks about available training
- User asks: "عندكم دورات؟"
- Need complete training list

**Example:**
```
User: "شو التدريبات المتاحة؟"
Agent calls: get_all_training_programs()
Result: List of 6 training programs
Agent: "لدينا 6 برامج تدريبية:
       1. التسويق الرقمي (45 ساعة)
       2. صناعة الأفلام (30 ساعة)
       ..."
```

### Tool 4: get_company_contact
**When to use:**
- User asks for address
- User asks for phone number
- User asks: "كيف أتواصل معكم؟"

**Example:**
```
User: "كيف أقدر أزوركم؟"
Agent calls: get_company_contact()
Result: Address, phone, social media
Agent: "عنواننا: دمشق - المزرعة - مقابل وزارة التربية
       رقمنا: 3349028"
```

---

## 🚀 Setup Instructions

### Step 1: Create Database Tables (REQUIRED)
```bash
# In Supabase SQL Editor, run:
create_ornina_complete_database.sql
```

**This creates 6 tables with 56+ records:**
- company_info (6 rows)
- work_areas (28 rows)
- target_markets (6 rows)
- products (6 rows)
- training_programs (6 rows)
- faqs (4 rows)

### Step 2: Verify Database
```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 check_supabase_tables.py
```

**Should see all 6 tables with data.**

### Step 3: Test Knowledge Base Manager
```bash
python3 knowledge_base_manager.py
```

**Expected output:**
```
🔍 Testing Knowledge Base Search...

Test 1: Search FAQs for 'أسعار'
Q: ما هي أسعار خدماتكم؟
A: أسعار خدماتنا تختلف حسب...

Test 2: Search Products for 'Call Center'
Product: Call Center بالذكاء الاصطناعي
...
```

### Step 4: Test MCP Tools
```bash
python3 local_mcp_server.py
```

**Expected output:**
```
📋 PHASE 1.5 MCP Server - Knowledge Base Search Active
Available tools: 4
  ✅ search_knowledge_base: ابحث في قاعدة المعرفة...
  ✅ get_all_products: احصل على قائمة بجميع المنتجات...
  ✅ get_all_training_programs: احصل على قائمة بجميع التدريبات...
  ✅ get_company_contact: احصل على معلومات الاتصال...
```

### Step 5: Start Agent
```bash
python3 agent.py dev
```

**Expected startup logs:**
```
🔧 تحميل 4 أداة محلية - Loading 4 local tools...
   ✅ search_knowledge_base: ابحث في قاعدة المعرفة...
   ✅ get_all_products: احصل على قائمة بجميع المنتجات...
   ✅ get_all_training_programs: احصل على قائمة بجميع التدريبات...
   ✅ get_company_contact: احصل على معلومات الاتصال...
```

---

## 🧪 Testing Scenarios

### Test 1: FAQ Search
**User says:** "ما هي أسعار خدماتكم؟"

**Expected behavior:**
1. Agent recognizes question
2. Calls `search_knowledge_base(query="أسعار")`
3. Finds FAQ about pricing
4. Returns answer from database

**What to look for in logs:**
```
📞 استدعاء أداة: search_knowledge_base - Calling tool
   المعاملات - Parameters: {'query': 'أسعار'}
   النتيجة - Result: True
```

### Test 2: List Products
**User says:** "شو الخدمات يلي عندكم؟"

**Expected behavior:**
1. Agent recognizes services question
2. Calls `get_all_products()`
3. Gets all 6 products from database
4. Lists them to user

**What to look for:**
- Agent mentions all 6 products
- Call Center, Films, Ads, Animation, Platform, Websites

### Test 3: Training Duration
**User says:** "كم مدة دورة التسويق الرقمي؟"

**Expected behavior:**
1. Agent searches for "التسويق الرقمي"
2. Finds training program
3. Reports: "45 ساعة"

### Test 4: Contact Info
**User says:** "كيف أقدر أتواصل معكم؟"

**Expected behavior:**
1. Agent calls `get_company_contact()`
2. Returns address, phone, social media
3. From database, not prompts

---

## 📊 Database Tables Used

| Table | Records | What Agent Can Query |
|-------|---------|---------------------|
| **faqs** | 4 | Pricing, online/offline, international, how to start |
| **products** | 6 | Call Center, Films, Ads, Animation, Platform, Websites |
| **training_programs** | 6 | Marketing, Films, UI/UX, Coding, Fashion, Web Dev |
| **work_areas** | 28 | All detailed service offerings |
| **company_info** | 6 | Address, phone, social media, about, vision, mission |
| **target_markets** | 6 | B2B, government, entrepreneurs, media, individuals, partnerships |

---

## ✅ Success Criteria

### Phase 1.5 is working if:
- [ ] Database tables exist with data
- [ ] Agent loads 4 MCP tools on startup
- [ ] Agent can search FAQs successfully
- [ ] Agent can list all products
- [ ] Agent can list all training programs
- [ ] Agent can provide contact info from database
- [ ] Search results show in agent logs
- [ ] Agent provides accurate answers from database

---

## 🐛 Troubleshooting

### Issue: Tools not loading
**Symptom:** Agent says "0 tools loaded"
**Fix:**
1. Check Supabase connection
2. Verify .env has SUPABASE_URL and SUPABASE_ANON_KEY
3. Restart agent

### Issue: Search returns no results
**Symptom:** search_knowledge_base returns empty
**Cause:** Database tables don't exist or are empty
**Fix:**
```bash
# Run SQL in Supabase:
create_ornina_complete_database.sql
```

### Issue: Import error for knowledge_base_manager
**Symptom:** "ModuleNotFoundError: No module named 'knowledge_base_manager'"
**Fix:**
```bash
# Make sure you're in the right directory:
cd /var/www/avatar\ /avatary
python3 agent.py dev
```

### Issue: Agent doesn't use tools
**Symptom:** Agent answers but never calls tools
**Cause:** Agent prefers prompts.py knowledge
**Solution:** This is OK! Agent only uses tools when needed.
- Try asking very specific questions
- Try: "كم مدة دورة التسويق بالضبط؟"

---

## 📈 What's Next (Phase 2)

After Phase 1.5 is working, we can add:
- Lead capture tool
- Save customer inquiries
- Consultation booking
- Training registration

---

## 📁 Files Changed/Created

| File | Status | Purpose |
|------|--------|---------|
| `knowledge_base_manager.py` | 🆕 NEW | Database search logic |
| `local_mcp_server.py` | ✏️ UPDATED | Added 4 search tools |
| `prompts.py` | ✏️ UPDATED | Added KB usage instructions |
| `PHASE1.5_KNOWLEDGE_BASE_SEARCH.md` | 🆕 NEW | This guide |

---

## 🎯 Quick Start Summary

```bash
# 1. Create database
# Run create_ornina_complete_database.sql in Supabase

# 2. Verify
cd /var/www/avatar\ /avatary
source venv/bin/activate
python3 check_supabase_tables.py

# 3. Test tools
python3 knowledge_base_manager.py
python3 local_mcp_server.py

# 4. Start agent
python3 agent.py dev

# 5. Test with user
# Ask: "ما هي أسعار خدماتكم؟"
# Ask: "شو الخدمات يلي عندكم؟"
# Ask: "كم مدة دورة التسويق؟"
```

**That's it! You now have dynamic database search! 🚀**
