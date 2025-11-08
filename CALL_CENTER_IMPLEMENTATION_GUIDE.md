# Call Center System - Implementation Guide

## Overview

A complete intelligent call center system built as a separate module from avatary. This system provides:

- **IVR (Interactive Voice Response)** with bilingual support (Arabic/English)
- **Smart Call Routing** to appropriate departments
- **Basic CRM System** with ticket management
- **Agent Dashboard** for real-time monitoring
- **Transcript Management** (text-only, no audio recording)
- **Rules Engine** that overrides avatary behavior when in call center mode
- **Glass UI** theme for modern, sleek appearance

## Project Structure

```
/callCenter/
├── __init__.py                      # Main package exports
├── config.py                        # Configuration & rules (override avatary)
├── models.py                        # Pydantic models (calls, tickets, agents)
├── rules_engine.py                  # Rules evaluation engine
├── call_router.py                   # IVR & routing logic
├── crm_system.py                    # CRM & ticket management
│
├── prompts/                         # Department-specific prompts
│   ├── __init__.py
│   ├── reception.py                 # Reception department (bilingual)
│   ├── sales.py                     # Sales department (bilingual)
│   └── complaints.py                # Complaints department (bilingual)
│
├── utils/                           # Helper functions
│   ├── __init__.py
│   └── call_utils.py                # Utilities (phone, email, formatting, etc.)
│
└── database/
    └── schema.sql                   # PostgreSQL database schema
```

## Key Components

### 1. Configuration System (`config.py`)

Centralized configuration with rules that override avatary behavior:

```python
from callCenter import config

# Check if call center mode is enabled
if config.CALL_CENTER_ENABLED:
    # Rules override avatary behavior
    config.AVATARY_OVERRIDES["disable_avatar_display"] = True
```

**Key Configuration Features:**
- Business hours definition
- Department configuration
- IVR settings (timeouts, retries)
- Rule definitions for each department
- Prompt templates (bilingual)
- Feature flags

### 2. Models (`models.py`)

Type-safe Pydantic models for all call center entities:

- `Call` - Represents a single call
- `Ticket` - Support tickets in CRM
- `Agent` - Agent/representative info
- `CustomerProfile` - Customer data
- `CallTranscript` - Call recordings (text only)
- `IVRStage` - Current IVR stage
- `Department` - Call departments (Reception, Sales, Complaints)

```python
from callCenter.models import Call, CallStatus, Department

call = Call(
    call_id="CALL_20240101120000_ABC123",
    phone_number="+966501234567",
    status=CallStatus.IVR_PROCESSING,
    department=Department.RECEPTION
)
```

### 3. Rules Engine (`rules_engine.py`)

Evaluates conditions and determines call center behavior:

```python
from callCenter.rules_engine import get_rules_engine

rules = get_rules_engine()

# Check if field is required
if rules.should_require_field("email"):
    # Collect email

# Route to department based on service type
routing_decision = rules.route_to_department("شكوى في الخدمة")
# Returns: RoutingDecision with department (COMPLAINTS) and confidence
```

**Main Responsibilities:**
- Validate user input
- Determine required fields
- Route to appropriate department
- Check if transfer to agent is needed
- Determine ticket priority
- Override avatary features

### 4. Call Router (`call_router.py`)

Manages IVR flow and call progression:

```python
from callCenter.call_router import get_call_router

router = get_call_router()

# Get welcome message
welcome = router.get_welcome_stage(language="ar")

# Get next IVR stage
next_stage = router.get_next_stage(current_stage)

# Route call to department
routing = router.route_call(service_type="شكوى")

# Process confirmation
result = router.process_confirmation("1")  # Press 1 to confirm
```

**IVR Stages:**
1. WELCOME - Initial greeting
2. COLLECT_NAME - Get customer name
3. COLLECT_PHONE - Get phone number
4. COLLECT_EMAIL - Get email
5. COLLECT_SERVICE_TYPE - Determine what they need
6. CONFIRM_DATA - Verify collected data
7. ROUTE_TO_DEPARTMENT - Determine which department
8. DEPARTMENT_HANDLING - Agent or bot handling
9. CALL_ENDED - Call completion

### 5. CRM System (`crm_system.py`)

Basic CRM for managing customers and tickets:

```python
from callCenter.crm_system import get_crm_system

crm = get_crm_system()

# Create or get customer
customer = await crm.create_or_update_customer(
    phone="+966501234567",
    name="أحمد محمد",
    email="ahmed@example.com"
)

# Create ticket automatically
ticket = await crm.create_ticket(
    customer_name="أحمد محمد",
    customer_phone="+966501234567",
    subject="مشكلة في التسليم",
    description="لم أستقبل طلبي بعد",
    department=Department.COMPLAINTS,
    priority=TicketPriority.HIGH
)

# Get open tickets
open_tickets = await crm.get_open_tickets(Department.COMPLAINTS)

# Assign to agent
await crm.assign_ticket(ticket.ticket_id, agent_id="AGENT_123")
```

**Features:**
- Customer profile management
- Ticket creation & tracking
- Auto-ticket creation from complaints
- Ticket assignment to agents
- Ticket status updates
- Customer history tracking

### 6. Department Prompts

Bilingual prompts for each department:

**Reception** (`prompts/reception.py`):
- Greeting messages
- Data collection prompts
- Validation messages
- Routing confirmations
- FAQ responses

**Sales** (`prompts/sales.py`):
- Service inquiries
- Pricing information
- Order processing
- FAQ search
- Offer suggestions

**Complaints** (`prompts/complaints.py`):
- Complaint collection
- Severity assessment
- Ticket creation
- Agent transfer
- Follow-up information

```python
from callCenter.prompts import get_reception_prompt

# Get prompt with variable substitution
msg = get_reception_prompt(
    "confirm_data",
    language="ar",
    name="أحمد",
    phone="0501234567",
    email="ahmed@example.com",
    service_type="مبيعات"
)
```

### 7. Utilities (`utils/call_utils.py`)

Helper functions:

```python
from callCenter.utils import (
    normalize_phone,
    validate_phone,
    generate_call_id,
    generate_ticket_id,
    detect_language,
    calculate_sentiment,
    get_department_name
)

# Phone utilities
normalized = normalize_phone("+966-50-123-4567")  # "9665012345678"
is_valid = validate_phone(normalized)  # True

# ID generation
call_id = generate_call_id()  # CALL_20240101120000_ABC123
ticket_id = generate_ticket_id()  # TKT_20240101_XYZ9

# Language detection
lang = detect_language("مرحبا hello")  # "mixed"
lang = detect_language("السلام عليكم")  # "ar"

# Sentiment analysis
sentiment = calculate_sentiment("الخدمة ممتازة", language="ar")  # "positive"
```

## Database Schema

PostgreSQL tables created via `database/schema.sql`:

### Main Tables
- `calls` - Call records with status, timing, routing info
- `customers` - Customer profiles
- `tickets` - Support tickets
- `tickets_history` - Audit trail for ticket changes
- `agents` - Agent/representative info
- `call_transcripts` - Text transcripts of calls
- `call_queue` - Queue management
- `department_daily_stats` - Analytics
- `agent_performance` - Performance metrics

### Views
- `active_calls` - Currently active calls
- `open_tickets` - Open support tickets
- `agent_availability` - Agent status and availability

## Integration with Avatary

The call center system is designed to work alongside avatary:

### Override Behavior

When `CALL_CENTER_MODE` is enabled:

```python
from callCenter import config, should_override_avatary

# These avatary features are disabled
if should_override_avatary("avatar_display"):
    # Don't show avatar

if should_override_avatary("visual_context"):
    # Don't analyze video frames

if should_override_avatary("tavus_avatar"):
    # Don't use Tavus visual avatar
```

### Reusable Components from Avatary

Keep using from avatary:
- ✅ LiveKit voice pipeline (STT/TTS)
- ✅ OpenAI LLM integration
- ✅ Conversation logging
- ✅ Supabase database connection
- ✅ Message handling
- ✅ Real-time voice communication

Disable in call center:
- ❌ Avatar visual display
- ❌ Face recognition (can be re-enabled for agent benefits)
- ❌ Visual context injection
- ❌ Tavus avatar integration

## Environment Variables

Add to `.env`:

```bash
# Call Center Mode
CALL_CENTER_MODE=enabled
COMPANY_NAME=Company Name
COMPANY_NAME_EN=Company Name (English)

# Business Hours
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00

# IVR Settings
IVR_MAX_RETRIES=3
IVR_TIMEOUT_SECONDS=30

# Database (reuse from avatary)
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# API Server
CALL_CENTER_API_PORT=8001
CALL_CENTER_API_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
CALL_CENTER_LOG_FILE=logs/call_center.log
```

## Workflow Example

### Complete Call Flow

```
1. Customer calls in → WebRTC connection established
2. IVR: Welcome message (bilingual)
3. IVR: Collect name
4. IVR: Collect phone
5. IVR: Collect email
6. IVR: Ask service type
7. IVR: Confirm data with customer
8. Rules Engine: Analyze service type
9. Route: Send to appropriate department
   - Sales keywords → SALES department
   - Complaint keywords → COMPLAINTS department
   - No match → RECEPTION department
10. Department Handling:
    - Sales: Bot answers FAQ or transfers to agent
    - Complaints: Auto-create ticket, transfer to agent
11. CRM: Log interaction, create records
12. Transcript: Save text transcript
13. Call End: Clean up, finalize records
```

### Sales Department Example

```python
from callCenter.prompts import search_faq

user_input = "ما هو سعر المنتج؟"

# Bot tries to handle with FAQ
answer = search_faq(user_input, language="ar")

if answer:
    # Bot responds
    respond_to_user(answer)
else:
    # Transfer to agent
    transfer_to_agent(department=Department.SALES)
```

### Complaints Department Example

```python
from callCenter.crm_system import get_crm_system
from callCenter.prompts import determine_severity

crm = get_crm_system()

# Collect complaint
complaint = await collect_complaint_data()

# Determine severity
severity = determine_severity(complaint.description)

# Create ticket with appropriate priority
ticket = await crm.create_ticket(
    customer_name=complaint.customer_name,
    customer_phone=complaint.customer_phone,
    subject=complaint.complaint_type,
    description=complaint.description,
    department=Department.COMPLAINTS,
    priority=get_priority_from_severity(severity)
)

# If urgent, immediately transfer to agent
if severity == "critical":
    transfer_to_agent(department=Department.COMPLAINTS)
```

## Frontend Implementation (Next Steps)

### Web Call Page (Glass UI)

Components needed:
- Call status indicator
- Real-time transcription display
- Customer info panel
- Call controls (hold, mute, transfer)
- Minimalist glass-morphism design

### Agent Dashboard

Real-time monitoring:
- Active calls list
- Queue status
- Customer info popup
- Ticket quick view
- Agent performance metrics

### CRM Dashboard

- Open tickets list
- Customer search
- Ticket details
- Ticket assignment
- Status tracking
- Analytics/reports

## Testing

### Test Cases

**Reception Stage:**
1. Collect all required data (name, phone, email, service)
2. Validate each field
3. Confirm data with customer
4. Route correctly based on service type

**Sales Department:**
1. Bot answers FAQ questions
2. Transfer complex inquiries
3. Record inquiry details

**Complaints Department:**
1. Auto-create tickets
2. Assess severity correctly
3. Show all info to agent
4. Create ticket history

**CRM:**
1. Create customers
2. Link tickets to customers
3. Update ticket status
4. Search tickets

### Running Tests

```python
# Test configuration
from callCenter import config
assert config.CALL_CENTER_ENABLED

# Test rules engine
from callCenter.rules_engine import get_rules_engine
rules = get_rules_engine()
assert rules.should_require_field("phone")

# Test router
from callCenter.call_router import get_call_router
router = get_call_router()
welcome = router.get_welcome_stage()
assert welcome.current_stage.value == "welcome"

# Test CRM
from callCenter.crm_system import get_crm_system
crm = get_crm_system()
customer = await crm.create_or_update_customer("+966501234567", "Test User")
assert customer is not None
```

## Performance Considerations

### Optimization Tips

1. **IVR Stages** - Keep responses quick
2. **Database** - Use indexes on frequently queried columns
3. **Transcripts** - Archive old transcripts to separate storage
4. **Cache** - Cache FAQ responses for sales department
5. **Queue** - Implement max queue size limits

### Scaling

- Use Redis for queue management (future phase)
- Implement load balancing for multiple agents
- Use connection pooling for database
- Archive old calls/tickets periodically

## Security Considerations

1. **Data Protection** - Phone, email, name are sensitive
2. **GDPR/CCPA** - Implement data retention policies
3. **Recording Consent** - Always ask before recording (future: audio)
4. **Agent Access** - Only show info when needed
5. **Encryption** - Use HTTPS/WSS for all communications

## Future Enhancements

### Phase 2 Features
- Twilio phone integration (PSTN)
- Multi-agent support with load balancing
- Audio recording with consent management
- Advanced CRM features
- Real-time analytics dashboard
- Sentiment analysis
- AI-powered auto-responses

### Phase 3 Features
- Skill-based routing
- VIP customer prioritization
- Integration with external CRMs
- SMS/Email notifications
- Interactive IVR menus
- Call recording playback
- Advanced reporting

## Support & Debugging

### Common Issues

**IVR Loop:**
- Check `IVR_MAX_RETRIES` setting
- Validate input processing logic

**Route to Wrong Department:**
- Check keywords in `config.py`
- Verify `route_to_department()` logic

**Ticket Not Created:**
- Verify `should_auto_create_ticket()` returns True
- Check database connection
- Verify customer exists

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("callCenter")
logger.info("Call created: CALL_123")
logger.error("Failed to create ticket", exc_info=True)
```

## File Checklist

Core Backend Files:
- ✅ `callCenter/__init__.py`
- ✅ `callCenter/config.py`
- ✅ `callCenter/models.py`
- ✅ `callCenter/rules_engine.py`
- ✅ `callCenter/call_router.py`
- ✅ `callCenter/crm_system.py`
- ✅ `callCenter/prompts/__init__.py`
- ✅ `callCenter/prompts/reception.py`
- ✅ `callCenter/prompts/sales.py`
- ✅ `callCenter/prompts/complaints.py`
- ✅ `callCenter/utils/__init__.py`
- ✅ `callCenter/utils/call_utils.py`
- ✅ `callCenter/database/schema.sql`

Frontend Files (Next):
- ⏳ `frontend/pages/CallPage.tsx` (glass UI)
- ⏳ `frontend/components/AgentDashboard.tsx`
- ⏳ `frontend/components/CRMDashboard.tsx`

## Next Steps

1. **Database Setup** - Run `schema.sql` in Supabase
2. **API Endpoints** - Create REST/WebSocket APIs
3. **Frontend Development** - Build web-based call page
4. **Integration Testing** - Test with avatary
5. **Performance Testing** - Load test the system

---

**Version:** 1.0.0
**Last Updated:** 2024
**Status:** Core Backend Complete, Frontend Pending
