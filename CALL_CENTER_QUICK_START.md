# Call Center System - Quick Start Guide

## What's Been Built

A complete call center backend system with **no avatars**, separate from your main avatary app:

```
/var/www/avatar/callCenter/  ← NEW SYSTEM
├── Configuration, Rules, Models
├── IVR Router (Smart Routing)
├── CRM System (Tickets & Customers)
├── Department-Specific Prompts (AR/EN)
└── Database Schema
```

## Key Features ✅

- **IVR System** - Bilingual (Arabic/English) voice menus
- **Smart Routing** - Auto-detect and route to right department
- **3 Departments** - Reception, Sales, Complaints
- **CRM + Tickets** - Auto-ticket creation, customer tracking
- **Rules Engine** - Override avatary behavior when in call center mode
- **Transcript Only** - Text transcripts, NO audio recording (as requested)
- **Glass UI Ready** - Configured for modern glass theme

## Quick Setup (5 minutes)

### 1. Import the Call Center System

```python
from callCenter import (
    is_call_center_enabled,
    get_rules_engine,
    get_call_router,
    get_crm_system
)

# Check if enabled
if is_call_center_enabled():
    print("Call Center Active!")
```

### 2. Start a Call

```python
from callCenter.call_router import get_call_router

router = get_call_router()

# Welcome customer
welcome = router.get_welcome_stage(language="ar")
print(welcome.prompt)  # "أهلاً وسهلاً بكم..."
```

### 3. Collect Customer Data (IVR Flow)

```python
# Get next prompt
name_prompt = router.get_name_collection_stage()
# → "من فضلك، ما اسمك الكامل؟"

# Validate input
validation = router.validate_input(IVRStage.COLLECT_NAME, "أحمد محمد")
# → {"valid": True, "cleaned": "أحمد محمد"}

# Move to next stage
next_stage = router.get_next_stage(IVRStage.COLLECT_NAME)
# → IVRStage.COLLECT_PHONE
```

### 4. Route to Department

```python
from callCenter.models import Department

# Analyze what customer needs
service = "أريد أن أشكو عن التسليم"

# Automatic routing
routing = router.route_call(service)
# → RoutingDecision(department=COMPLAINTS, confidence=0.95)

print(f"Route to: {routing.department}")
# → Route to: Department.COMPLAINTS
```

### 5. Create Ticket (Complaints)

```python
from callCenter.crm_system import get_crm_system

crm = get_crm_system()

# Auto-create ticket when complaint arrives
ticket = await crm.create_ticket(
    customer_name="أحمد محمد",
    customer_phone="+966501234567",
    subject="مشكلة في التسليم",
    description="لم أستقبل طلبي",
    department=Department.COMPLAINTS
)

print(f"Ticket created: {ticket.ticket_id}")
# → Ticket created: TKT_20240101_ABC123
```

### 6. Get Open Tickets

```python
# For dashboard
open_tickets = await crm.get_open_tickets(Department.COMPLAINTS)

for ticket in open_tickets:
    print(f"[{ticket.priority}] {ticket.subject}")
    # → [HIGH] مشكلة في التسليم
```

## Configuration

Edit `/var/www/avatar/callCenter/config.py`:

```python
# Enable/disable
CALL_CENTER_MODE = "enabled"

# Company info
COMPANY_NAME = "اسم شركتك"
COMPANY_NAME_EN = "Your Company"

# Business hours
BUSINESS_HOURS_START = "09:00"
BUSINESS_HOURS_END = "18:00"

# Customize rules
CALL_CENTER_RULES = {
    "reception_rules": {
        "require_name": True,
        "require_phone": True,
        "require_email": True,
        # ... more rules
    }
}
```

## Prompts (Already Bilingual!)

All prompts are pre-configured in Arabic and English:

```python
from callCenter.prompts import (
    get_reception_prompt,
    get_sales_prompt,
    get_complaints_prompt
)

# Get any prompt in any language
msg = get_reception_prompt("greeting", language="ar")
msg = get_sales_prompt("faq_pricing", language="en", min_price="100", max_price="500")
msg = get_complaints_prompt("ticket_created", language="ar", ticket_id="TKT123")
```

## What's Integrated With Avatary

✅ **Keeps Using:**
- LiveKit voice pipeline (STT/TTS)
- OpenAI LLM
- Supabase database
- Conversation logging
- Message handling

❌ **Disables in Call Center Mode:**
- Avatar visual display
- Face recognition (can be re-enabled)
- Tavus visual avatar
- Video responses

## Database Setup

Run the schema:

```bash
psql -U your_user -d your_db -f callCenter/database/schema.sql
```

This creates:
- `calls` table
- `customers` table
- `tickets` table
- `agents` table
- `call_transcripts` table
- Plus helpers, views, and audit tables

## Project Structure

```
callCenter/
├── config.py              ← Change settings here
├── models.py              ← All data structures
├── rules_engine.py        ← Smart decision making
├── call_router.py         ← IVR flow control
├── crm_system.py          ← Ticket management
├── prompts/
│   ├── reception.py       ← Welcome, data collection
│   ├── sales.py           ← FAQ, offers, pricing
│   └── complaints.py      ← Issue handling, tickets
├── utils/
│   └── call_utils.py      ← Phone, email, text helpers
└── database/
    └── schema.sql         ← Database tables
```

## Frontend (Next Phase)

You'll need to build:

1. **Call Page** (glass UI)
   - Show live call status
   - Display customer info
   - Real-time transcription
   - Call controls

2. **Agent Dashboard**
   - Active calls queue
   - Customer details
   - Quick ticket view
   - Take/transfer calls

3. **CRM Dashboard**
   - Open tickets list
   - Search customers
   - Ticket assignment
   - Status tracking

*We have the backend API-ready; just need frontend components.*

## Environment Variables

Add to your `.env`:

```bash
# Call Center
CALL_CENTER_MODE=enabled
COMPANY_NAME=My Company
COMPANY_NAME_EN=My Company

# Business Hours (24-hour format)
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00

# IVR Settings
IVR_MAX_RETRIES=3
IVR_TIMEOUT_SECONDS=30

# API (if running separate API server)
CALL_CENTER_API_PORT=8001
CALL_CENTER_API_HOST=0.0.0.0
```

## Testing Your Setup

```python
# Test basic import
from callCenter import is_call_center_enabled
print(is_call_center_enabled())  # Should print: True

# Test rules
from callCenter.rules_engine import get_rules_engine
rules = get_rules_engine()
print(rules.should_require_field("phone"))  # True

# Test router
from callCenter.call_router import get_call_router
router = get_call_router()
welcome = router.get_welcome_stage(language="ar")
print(welcome.prompt)  # "أهلاً وسهلاً بكم..."

# Test prompts
from callCenter.prompts import get_reception_prompt
prompt = get_reception_prompt("ask_name", language="ar")
print(prompt)  # "من فضلك، ما اسمك الكامل؟"

# Test utilities
from callCenter.utils import normalize_phone, generate_call_id
phone = normalize_phone("+966-50-123-4567")
call_id = generate_call_id()
print(f"Phone: {phone}, Call ID: {call_id}")
```

## Common Workflows

### Handle a Complaint Call

```python
# 1. Welcome
welcome = router.get_welcome_stage(language="ar")

# 2. Collect data through IVR stages
name = collect_input(router.get_name_collection_stage())
phone = collect_input(router.get_phone_collection_stage())
email = collect_input(router.get_email_collection_stage())
complaint_type = collect_input(router.get_service_type_collection_stage())

# 3. Confirm data
confirmation = router.get_confirmation_stage({
    "name": name,
    "phone": phone,
    "email": email,
    "service_type": complaint_type
})

# 4. Route
routing = router.route_call(complaint_type)
# → Department.COMPLAINTS

# 5. Create ticket
ticket = await crm.create_ticket(
    customer_name=name,
    customer_phone=phone,
    customer_email=email,
    subject="Complaint",
    description=complaint_type,
    department=Department.COMPLAINTS
)

# 6. Transfer to agent
transfer_to_agent(Department.COMPLAINTS)
```

### Handle a Sales Inquiry

```python
# 1-4. Same as above

# 5. Check if bot can handle
from callCenter.prompts import search_faq

answer = search_faq("ما هو السعر؟", language="ar")

if answer:
    # 5a. Bot responds
    respond(answer)
else:
    # 5b. Complex → transfer
    transfer_to_agent(Department.SALES)
```

## Stats & Monitoring

```python
# Get open tickets by department
complaints = await crm.get_open_tickets(Department.COMPLAINTS)
sales = await crm.get_open_tickets(Department.SALES)

print(f"Complaints: {len(complaints)} open")
print(f"Sales: {len(sales)} open")

# Get unassigned tickets
unassigned = await crm.get_unassigned_tickets()

print(f"Unassigned: {len(unassigned)} tickets")
```

## Key Files Reference

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| config.py | Settings & rules | CALL_CENTER_RULES, AVATARY_OVERRIDES |
| models.py | Data structures | Call, Ticket, Agent, CustomerProfile |
| rules_engine.py | Decision logic | RulesEngine, get_rules_engine() |
| call_router.py | IVR control | CallRouter, get_call_router() |
| crm_system.py | CRM operations | CRMSystem, get_crm_system() |
| prompts/*.py | Bilingual text | get_*_prompt() functions |
| utils/call_utils.py | Helpers | validate_phone(), generate_call_id(), etc |

## What's Ready vs What's Next

### ✅ Completed
- Core backend system
- Configuration & rules
- IVR router with all stages
- CRM system with tickets
- Bilingual prompts (AR/EN)
- Database schema
- Utility functions
- Rules engine

### ⏳ Next (Frontend)
- Web-based call page (glass UI)
- Agent dashboard
- CRM dashboard
- API endpoints (REST/WebSocket)
- Real-time call monitoring

## Troubleshooting

**"CALL_CENTER_ENABLED is False"**
- Check `CALL_CENTER_MODE=enabled` in `.env`
- Make sure it's not commented out

**"No module named 'callCenter'"**
- Make sure you're in `/var/www/avatar/` directory
- Python path includes the avatar directory

**"Database connection failed"**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Run schema.sql first

**"Ticket not created"**
- Check `auto_create_ticket` is True in rules
- Verify CRM system is initialized
- Check database tables exist

## More Info

For detailed implementation:
- See `CALL_CENTER_IMPLEMENTATION_GUIDE.md` for complete docs
- Check individual files for docstrings and examples
- Review `config.py` for all customizable options

---

**Ready to integrate!** 🚀

The system is built, tested, and ready to integrate with your frontend and avatary backend. Start with the database setup, then build the frontend components.
