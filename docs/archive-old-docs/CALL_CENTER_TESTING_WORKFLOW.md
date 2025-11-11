# Call Center Testing Workflow - Ornina Integration

## 🎯 Overview

Test the Call Center system using the same workflow as Avatar with:
- **Same knowledge base** (Ornina company info, services, training programs)
- **Same prompts** (`prompts.py` from avatary)
- **Same Supabase database** for customer data
- **Routing logic**: Reception → Sales OR Complaints department
- **Communication**: Arabic/English bilingual support

---

## 📊 Current Architecture

### Avatar System (Video Call)
```
/var/www/avatar /avatary/
├── agent.py              ← Main agent logic
├── prompts.py            ← Ornina knowledge base
├── models.py             ← Data models
├── save_transcript_api.py ← Transcript storage
└── [face recognition, vision, etc]
```

### Call Center System (IVR + Routing)
```
/var/www/avatar /callCenter/
├── api.py                ← FastAPI endpoints
├── call_router.py        ← 9-stage IVR
├── crm_system.py         ← Ticket management
├── config.py             ← Ornina config
├── prompts/              ← Bilingual prompts (needs Ornina data)
└── models.py             ← Call/Ticket models
```

### Shared Data
```
Supabase Database:
├── customers            ← Customer data (same as Avatar)
├── conversations        ← Transcripts (same as Avatar)
├── appointments         ← Bookings (same as Avatar)
└── call_logs           ← New: Call center logs
```

---

## 🔄 Integration Steps

### Step 1: Update Call Center Config with Ornina Data

The Call Center should use the same company information as Avatar.

**Current**: `/var/www/avatar /callCenter/config.py`
**Should contain**: Same data as `/var/www/avatar /avatary/prompts.py`

Key data to synchronize:
- Company name: Ornina
- Address: Syria - Damascus - Al Mezzeh - opposite Ministry of Education
- Phone: 3349028
- Services: Call Center, Video Production, AI Ads, 2D/3D Animation, Digital Platform, Website Design
- Training programs: Digital Marketing, Film Production, UI/UX Design, Coding, Fashion Design, Web Design

### Step 2: Update Call Center Prompts with Ornina Knowledge

**File**: `/var/www/avatar /callCenter/prompts/` (already exists with reception.py, sales.py, complaints.py)

Should contain same information as:
- `prompts.py` → AGENT_INSTRUCTIONS

Current structure:
```
callCenter/prompts/
├── reception.py         ← Greeting + info collection
├── sales.py            ← Upsell services
└── complaints.py       ← Handle issues
```

### Step 3: Connect to Same Supabase Database

**Configuration**: Both systems should use same database connection

```python
# In callCenter/config.py
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Same tables as Avatar:
# - customers
# - conversations
# - appointments
# - call_logs (new)
```

### Step 4: Implement Routing Logic

**Call Flow**:
```
Customer Calls
    ↓
Reception (GREETING & INFO COLLECTION)
    ├─ Collect: Name, Phone, Email, Company
    ├─ Understand: What do they need?
    ├─ Offer: Info about services
    └─ Route Decision:
        ├─ SALES → Customer wants service info (Route to Sales)
        ├─ COMPLAINTS → Customer has issue (Route to Complaints)
        └─ INFORMATION → Just needs company info (End call)
    ↓
Sales OR Complaints (SPECIALIZED HANDLING)
    ├─ SALES: Explain service details, offer consultation
    ├─ COMPLAINTS: Understand issue, create ticket
    └─ Create transcript + Ticket
    ↓
Escalate to Agent (OPTIONAL)
    ├─ Create Supabase ticket
    ├─ Assign to agent
    └─ Send notification
```

### Step 5: Testing Workflow

**Scenario 1: Service Inquiry (Sales)**
```
1. Call → Reception answers in Arabic
2. Greeting: "السلام عليكم! أهلاً بك في شركة أورنينا"
3. Question: "كيف بقدر ساعدك اليوم؟"
4. Customer: "أنا مهتم بخدمة الذكاء الاصطناعي للإعلانات"
5. Reception → Route to SALES
6. Sales: Explain AI Ads service
7. Collect contact info + create ticket
8. End call with follow-up email
```

**Scenario 2: Complaint/Issue (Complaints)**
```
1. Call → Reception answers
2. Customer: "عندي مشكلة مع خدمة سابقة"
3. Reception → Route to COMPLAINTS
4. Complaints: "حكي لي عن المشكلة"
5. Create support ticket
6. Assign to agent
7. Store transcript in Supabase
```

**Scenario 3: Training Program Inquiry**
```
1. Call → Reception
2. Customer: "أريد معلومات عن برنامج التدريب"
3. Reception: Provide program details
4. Collect info for consultant
5. Create appointment in Supabase
```

---

## 🛠️ Technical Integration Points

### 1. Update callCenter/config.py

Add Ornina company data:

```python
COMPANY_INFO = {
    "name": "Ornina",
    "arabic_name": "شركة أورنينا للذكاء الاصطناعي والحلول الرقمية",
    "address": "Syria - Damascus - Al Mezzeh - opposite Ministry of Education",
    "phone": "3349028",
    "social_media": {
        "tiktok": "@ornina.official",
        "facebook": "@orninaofficial",
        "youtube": "@orninaofficial"
    }
}

SERVICES = [
    {
        "name": "Call Center AI",
        "arabic": "Call Center بالذكاء الاصطناعي",
        "description": "24/7 Smart automatic response system"
    },
    # ... more services
]

TRAINING_PROGRAMS = [
    {
        "name": "Digital Marketing Mastery",
        "hours": 45,
        "topics": ["Prompt Engineering", "Content Creation", "SEO"]
    },
    # ... more programs
]
```

### 2. Update callCenter/prompts/reception.py

Connect to Avatar's knowledge:

```python
from prompts import AGENT_INSTRUCTIONS

# Use same instructions as Avatar
RECEPTION_PROMPT = AGENT_INSTRUCTIONS + """

=== Reception Flow ===
1. Welcome in Arabic
2. Collect: Name, Phone, Email
3. Identify: What does customer need?
4. Route:
   - If asking about service → SALES
   - If has complaint → COMPLAINTS
   - If just info → Answer directly
"""
```

### 3. Implement Supabase Integration

```python
from supabase import create_client

# Same connection as Avatar
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

async def save_call_transcript(call_data):
    """Save to same database as Avatar"""
    await supabase.table("conversations").insert({
        "customer_name": call_data["name"],
        "customer_phone": call_data["phone"],
        "type": "call_center",  # vs "video" for Avatar
        "department": call_data["department"],
        "transcript": call_data["transcript"],
        "created_at": datetime.now()
    })

async def create_ticket(customer_info, issue):
    """Create ticket linked to customer"""
    # Check if customer exists
    customer = await supabase.table("customers").select("*").eq(
        "phone", customer_info["phone"]
    ).execute()

    # Create ticket
    await supabase.table("call_logs").insert({
        "customer_id": customer[0]["id"] if customer else None,
        "department": issue["department"],
        "priority": issue["priority"],
        "description": issue["description"],
        "status": "open"
    })
```

### 4. Update Call Router for Ornina Workflow

```python
# callCenter/call_router.py
async def route_call(transcript):
    """
    Route based on content analysis
    Same logic as Avatar's conversation flow
    """

    # Stage 1: GREETING (like Avatar)
    greeting_response = await generate_greeting(transcript)

    # Stage 2: COLLECT INFO (like Avatar)
    customer_info = await extract_info(transcript)

    # Stage 3: IDENTIFY NEED
    intent = await identify_intent(transcript)

    # Stage 4: ROUTE
    if intent in ["sales", "service_info"]:
        return "SALES"
    elif intent in ["complaint", "issue", "problem"]:
        return "COMPLAINTS"
    else:
        return "INFORMATION"
```

---

## 📝 Testing Checklist

### Backend Setup
- [ ] Update callCenter/config.py with Ornina data
- [ ] Update callCenter/prompts/ with Ornina knowledge
- [ ] Connect to same Supabase database (copy .env from avatary)
- [ ] Test database connection
- [ ] Verify call routing logic

### API Endpoints
- [ ] POST /api/calls - Initiate call with customer info
- [ ] GET /api/calls/{call_id} - Retrieve call details
- [ ] POST /api/calls/{call_id}/route - Route to department
- [ ] POST /api/tickets - Create ticket from call
- [ ] GET /api/transcripts/{call_id} - Get transcript

### Frontend Testing
- [ ] Start Call page: Customer can dial/chat
- [ ] Agent Dashboard: See routing status
- [ ] CRM Dashboard: View tickets created from calls
- [ ] Real-time updates via WebSocket

### Database Testing
- [ ] Customer info saved to Supabase
- [ ] Conversation transcript saved
- [ ] Tickets linked to customers
- [ ] Cross-reference with Avatar calls

---

## 🧪 Manual Test Scenarios

### Test 1: Service Inquiry Flow

```bash
# Start Call Center
cd "/var/www/avatar /"
./start-call-center.sh

# In another terminal, simulate call
curl -X POST "http://localhost:8000/api/calls" \
  -d "phone_number=+966501234567&customer_name=علي محمد"

# Get call ID
CALL_ID="CALL-XXXXXXXX"

# Send message simulating Reception
curl -X POST "http://localhost:8000/api/transcripts/${CALL_ID}/messages" \
  -d "speaker=bot&content=السلام عليكم، كيف بقدر ساعدك؟&language=ar"

# Send customer response
curl -X POST "http://localhost:8000/api/transcripts/${CALL_ID}/messages" \
  -d "speaker=customer&content=أريد معلومات عن خدمة الإعلانات الذكية&language=ar"

# Route to Sales
curl -X POST "http://localhost:8000/api/calls/${CALL_ID}/route" \
  -d "department=sales"

# Verify ticket created
curl http://localhost:8000/api/tickets
```

### Test 2: Complaint Flow

```bash
# Similar to above but with complaint message
curl -X POST "http://localhost:8000/api/transcripts/${CALL_ID}/messages" \
  -d "speaker=customer&content=عندي مشكلة مع طلبي السابق&language=ar"

# Route to Complaints
curl -X POST "http://localhost:8000/api/calls/${CALL_ID}/route" \
  -d "department=complaints"

# Create ticket
curl -X POST "http://localhost:8000/api/tickets" \
  -d "customer_name=علي محمد&customer_phone=%2B966501234567&subject=مشكلة في الطلب&description=عدم استلام الخدمة&priority=high"
```

### Test 3: Frontend Integration

```bash
# Navigate to Call Center Hub
http://localhost:3000/callcenter

# 1. Click "Start Call"
# 2. Simulate conversation:
#    - Greeting: "السلام عليكم!"
#    - Customer responds with inquiry
#    - System routes to appropriate department
# 3. Check Agent Dashboard for routing
# 4. Verify CRM Dashboard shows new ticket
```

---

## 🔐 Data Synchronization

### Same Data Sources

| Data | Avatar Source | Call Center Source | Database |
|------|---------------|-------------------|----------|
| Company Info | prompts.py | config.py | Supabase |
| Services | prompts.py | config.py | Supabase |
| Training Programs | prompts.py | config.py | Supabase |
| Customers | agent.py | call_router.py | Supabase.customers |
| Conversations | save_transcript_api.py | call_router.py | Supabase.conversations |
| Tickets | local_mcp_server.py | crm_system.py | Supabase.call_logs |

### Environment Variables (shared)

```bash
# Copy from /var/www/avatar /avatary/.env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxx
```

---

## 🎓 Expected Behavior

### Reception Phase
- **Input**: Customer calls
- **Output**: Customer info collected, intent identified
- **Database**: Customer record created/updated
- **Duration**: 30-60 seconds

### Routing Phase
- **Input**: Customer intent
- **Output**: Route to Sales, Complaints, or Info
- **Logic**: Same as Avatar conversation flow
- **Duration**: Automatic

### Department Phase
- **Sales**: Present services, collect details
- **Complaints**: Understand issue, create ticket
- **Duration**: 2-5 minutes

### Resolution Phase
- **Output**: Transcript saved, ticket created (if needed)
- **Database**: Call logged, ticket linked to customer
- **Follow-up**: Email/SMS to customer

---

## 📊 Success Metrics

Track these KPIs:

- [ ] Call success rate (completed/total)
- [ ] Average routing time
- [ ] Customer satisfaction (from transcript)
- [ ] Ticket creation rate
- [ ] Database sync accuracy
- [ ] Response time (< 2 seconds)
- [ ] Language accuracy (Arabic/English)

---

## 🚀 Deployment

### Prerequisites
- [ ] Supabase credentials (.env updated)
- [ ] Ornina data in config
- [ ] Prompts synchronized
- [ ] Database tables created
- [ ] Avatar system running (for reference)

### Startup Command
```bash
cd "/var/www/avatar /"

# Terminal 1: Call Center API
cd callCenter
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Monitor logs (optional)
tail -f /tmp/call-center-backend.log
```

### Verify Integration
```bash
# Check API health
curl http://localhost:8000/health

# Check Supabase connection
curl http://localhost:8000/api/customers

# Check WebSocket
# Open browser → http://localhost:3000/callcenter
# Open DevTools → check WebSocket connection
```

---

## 📖 Documentation Files

Already created:
- `README_CALL_CENTER.md` - Main index
- `CALL_CENTER_GETTING_STARTED.md` - Setup guide
- `CALL_CENTER_API_INTEGRATION.md` - API reference
- `QUICK_COMMANDS.md` - Commands

This file:
- `CALL_CENTER_TESTING_WORKFLOW.md` - Testing guide

---

## 🎯 Next Steps

1. **Synchronize Data**
   - Copy Ornina company info to callCenter/config.py
   - Copy prompts from avatary/prompts.py to callCenter/prompts/

2. **Setup Database**
   - Copy .env from avatary to callCenter
   - Test Supabase connection

3. **Run Tests**
   - Execute test scenarios above
   - Verify routing logic
   - Check database updates

4. **Monitor**
   - Check logs for errors
   - Verify transcripts are saved
   - Confirm tickets are created

---

**Status**: Ready to test
**Date**: November 8, 2025
**Version**: 1.0.0
