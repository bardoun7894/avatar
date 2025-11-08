# Call Center Testing Guide

**Date**: November 8, 2025
**Version**: 1.0
**Status**: Ready for Testing

---

## Prerequisites

### 1. Environment Setup

✅ **Done**: `.env` file created with Supabase credentials copied from Avatar

**Location**: `/var/www/avatar /callCenter/.env`

**Key variables configured**:
- `SUPABASE_URL` - Database connection
- `SUPABASE_KEY` - Database authentication
- `OPENAI_API_KEY` - For AI responses
- `ELEVENLABS_API_KEY` - For voice generation
- `DEFAULT_LANGUAGE=ar` - Arabic as default

### 2. Dependencies

```bash
cd "/var/www/avatar /callCenter"
pip install -r requirements.txt
```

**Requirements**:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- python-multipart==0.0.6
- pydantic==2.5.0
- websockets==12.0
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- python-dotenv==1.0.0

### 3. Directory Structure

```
/var/www/avatar /
├── callCenter/
│   ├── .env                    ← Environment variables (created)
│   ├── api.py                  ← FastAPI application (35+ endpoints)
│   ├── main.py                 ← Entry point
│   ├── config.py               ← Configuration with Ornina data
│   ├── call_router.py          ← IVR routing logic
│   ├── models.py               ← Pydantic models
│   ├── crm_system.py           ← Ticket management
│   ├── prompts/
│   │   ├── routing_prompts.py  ← NEW: Routing with personas
│   │   ├── reception.py        ← Reception messages
│   │   ├── sales.py            ← Sales messages
│   │   └── complaints.py       ← Complaints messages
│   ├── utils/
│   ├── database/
│   └── requirements.txt
└── .gitignore                  ← Prevents .env being committed
```

---

## Testing the Call Center

### 1. Start the Application

**Option A: Automated Script**

```bash
cd "/var/www/avatar "
chmod +x start-call-center.sh
./start-call-center.sh
```

**Option B: Manual Start**

```bash
# Terminal 1: Backend API
cd "/var/www/avatar /callCenter"
python main.py

# Expected output:
# Uvicorn running on http://0.0.0.0:8001
# Application startup complete
```

### 2. Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8001/health

# Expected response:
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-11-08T10:30:00Z"
}
```

### 3. Test Routing Prompts (New Feature)

**Import in Python**:

```python
from callCenter.call_router import get_call_router

router = get_call_router()

# Test 1: Service Inquiry Detection
message = "أنا مهتم بخدمة الإعلانات"
intent = router.detect_intent_from_message(message, language="ar")
print(f"Intent: {intent}")  # IntentEnum.SERVICE_INQUIRY

department = router.route_by_detected_intent(intent)
print(f"Route to: {department}")  # DepartmentEnum.SALES

# Test 2: Get Routing Decision (Pydantic model)
routing = router.get_intent_routing_decision(
    call_id="TEST-001",
    message=message,
    language="ar"
)
print(f"Department: {routing.intent_detection.department.value}")
print(f"Confidence: {routing.intent_detection.confidence}")

# Test 3: Get Department Persona
persona = router.get_department_persona(routing.intent_detection.department)
print(f"Persona Name: {persona.name_ar}")
print(f"Tone: {persona.tone_ar}")
```

### 4. Test Department Prompts

**Reception Prompts**:

```bash
# Arabic greeting
curl "http://localhost:8001/api/prompts/reception/greeting?language=ar"

# Response:
# السلام عليكم! أهلاً بك في شركة أورنينا...
```

**Sales Prompts**:

```bash
# Service explanation
curl "http://localhost:8001/api/prompts/sales/service_ai_call_center?language=ar"

# Response:
# نظام ذكي للرد التلقائي على العملاء 24/7...
```

**Complaints Prompts**:

```bash
# Welcome message
curl "http://localhost:8001/api/prompts/complaints/welcome?language=ar"

# Response:
# السلام عليكم! أنا من قسم معالجة الشكاوى...
```

---

## Test Scenarios

### Scenario 1: Service Inquiry → Sales Route

**Flow**: Reception → Detect Service Inquiry → Route to Sales

```bash
# Start a call
CALL_ID="CALL-SERVICE-001"

# Step 1: Initiate call
curl -X POST "http://localhost:8001/api/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+966501234567",
    "customer_name": "علي محمد"
  }'

# Response: { "call_id": "CALL-SERVICE-001", "status": "initiated" }

# Step 2: Send customer intent message
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker": "customer",
    "content": "أنا مهتم بخدمة الإعلانات الذكية",
    "language": "ar"
  }'

# Step 3: Detect intent and route
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "أنا مهتم بخدمة الإعلانات الذكية",
    "language": "ar"
  }'

# Expected response:
{
  "call_id": "CALL-SERVICE-001",
  "intent": "service_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم المبيعات...",
  "persona": {
    "name_ar": "فريق المبيعات",
    "tone_ar": "متحمس، إيجابي، مقنع، متخصص",
    "expertise_ar": ["شرح الخدمات", "تقديم العروض", ...]
  }
}
```

### Scenario 2: Complaint → Complaints Route

**Flow**: Reception → Detect Complaint → Route to Complaints

```bash
CALL_ID="CALL-COMPLAINT-001"

# Step 1: Initiate call
curl -X POST "http://localhost:8001/api/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+966502234567",
    "customer_name": "فاطمة علي"
  }'

# Step 2: Send complaint message
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker": "customer",
    "content": "عندي مشكلة مع طلبي السابق، لم استقبل الخدمة",
    "language": "ar"
  }'

# Step 3: Detect intent and route
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "عندي مشكلة مع طلبي السابق",
    "language": "ar"
  }'

# Expected response:
{
  "call_id": "CALL-COMPLAINT-001",
  "intent": "complaint",
  "department": "complaints",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم معالجة الشكاوى...",
  "persona": {
    "name_ar": "فريق معالجة الشكاوى",
    "tone_ar": "متعاطف، هادئ، حازم، موثوق",
    "expertise_ar": ["الاستماع الفعّال", "حل المشاكل", ...]
  }
}
```

### Scenario 3: Training Inquiry → Sales Route

**Flow**: Reception → Detect Training Inquiry → Route to Sales

```bash
CALL_ID="CALL-TRAINING-001"

# Step 1: Initiate call
curl -X POST "http://localhost:8001/api/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+966503234567",
    "customer_name": "محمد أحمد"
  }'

# Step 2: Send training inquiry
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker": "customer",
    "content": "أريد معلومات عن برنامج التسويق الرقمي",
    "language": "ar"
  }'

# Step 3: Detect intent and route
curl -X POST "http://localhost:8001/api/calls/$CALL_ID/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "أريد معلومات عن برنامج التسويق الرقمي والتدريب",
    "language": "ar"
  }'

# Expected response:
{
  "call_id": "CALL-TRAINING-001",
  "intent": "training_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم المبيعات...",
  "persona": {
    "name_ar": "فريق المبيعات",
    "tone_ar": "متحمس، إيجابي، مقنع، متخصص"
  }
}
```

### Scenario 4: English Language Support

```bash
# Same as above but in English
curl -X POST "http://localhost:8001/api/calls/CALL-EN-001/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am interested in your smart ads service",
    "language": "en"
  }'

# Expected response (in English):
{
  "call_id": "CALL-EN-001",
  "intent": "service_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "routing_message": "Hello! I'm from the Sales department...",
  "persona": {
    "name_en": "Sales Team",
    "tone_en": "Enthusiastic, positive, persuasive, expert"
  }
}
```

---

## Testing with Supabase

### 1. Verify Database Connection

```bash
# Test Supabase connection via API
curl "http://localhost:8001/api/health/database"

# Expected response:
{
  "database_connected": true,
  "database_name": "postgres",
  "tables_available": ["customers", "conversations", "call_logs", ...]
}
```

### 2. Save Call to Supabase

```bash
CALL_ID="CALL-DB-001"

# Initiate call
curl -X POST "http://localhost:8001/api/calls" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+966501234567",
    "customer_name": "أحمد علي",
    "email": "ahmad@example.com",
    "save_to_db": true
  }'

# Verify in Supabase:
# SELECT * FROM call_logs WHERE call_id = 'CALL-DB-001';
```

---

## Integration Testing

### 1. Test Ornina Company Data

```bash
# Get all services
curl "http://localhost:8001/api/config/services?language=ar"

# Response should include:
# - Call Center بالذكاء الاصطناعي
# - إنتاج الأفلام والمسلسلات
# - الإعلانات الذكية
# - الأنيميشن 2D/3D
# - المنصة الرقمية الشاملة
# - تصميم وبرمجة المواقع

# Get all training programs
curl "http://localhost:8001/api/config/training-programs?language=ar"

# Response should include all 6 training programs
```

### 2. Test WebSocket Real-Time Routing

```bash
# Connect WebSocket
wscat -c ws://localhost:8001/ws/calls/CALL-WS-001

# Send routing request
{
  "type": "detect_intent",
  "message": "أريد خدمة تصميم موقع",
  "language": "ar"
}

# Receive real-time routing response
{
  "type": "routing_result",
  "intent": "service_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "persona": { ... }
}
```

---

## Debugging

### 1. Check Logs

```bash
# Backend logs
tail -f "/var/www/avatar /callCenter/logs/call_center.log"

# Check for errors
grep ERROR "/var/www/avatar /callCenter/logs/call_center.log"
```

### 2. Test Pydantic Models

```python
from callCenter.prompts.routing_prompts import (
    CustomerInfo,
    IntentDetection,
    RoutingDecision,
    IntentEnum,
    DepartmentEnum
)

# Test CustomerInfo model
customer = CustomerInfo(
    name="اسم",
    phone="+966501234567"
)
print(customer.model_dump_json())  # JSON output

# Test IntentDetection model
intent = IntentDetection(
    intent=IntentEnum.SERVICE_INQUIRY,
    department=DepartmentEnum.SALES,
    confidence=0.95,
    keywords=["خدمة", "عندكم"],
    reasoning="Service inquiry detected"
)
print(intent.model_dump())  # Dict output
```

### 3. Validate Configuration

```bash
# Check if .env is loaded
curl "http://localhost:8001/api/config/verify"

# Should return:
{
  "supabase_connected": true,
  "openai_configured": true,
  "call_center_enabled": true,
  "ornina_data_loaded": true,
  "routing_prompts_loaded": true
}
```

---

## Expected Test Results

### ✅ Passing Tests

- [ ] Environment variables loaded from `.env`
- [ ] Supabase connection successful
- [ ] Service inquiry → Routes to SALES
- [ ] Complaint → Routes to COMPLAINTS
- [ ] Training inquiry → Routes to SALES
- [ ] Reception persona greeting works
- [ ] Sales persona service explanations work
- [ ] Complaints persona welcome message works
- [ ] Arabic language support functional
- [ ] English language support functional
- [ ] Confidence scoring accurate
- [ ] WebSocket real-time updates working
- [ ] Pydantic models validate correctly
- [ ] Company information displays correctly
- [ ] Training programs listed accurately

### ⚠️ Common Issues

**Issue**: `ModuleNotFoundError: No module named 'callCenter'`
- **Solution**: Ensure you're in correct directory and have run `pip install -r requirements.txt`

**Issue**: `No module named 'dotenv'`
- **Solution**: Run `pip install python-dotenv`

**Issue**: `SUPABASE_URL not configured`
- **Solution**: Check `.env` file exists and has correct credentials from avatary

**Issue**: `Connection refused localhost:8001`
- **Solution**: Ensure backend is running with `python main.py`

---

## Testing Checklist

### Core Functionality
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200
- [ ] Environment variables loaded

### Intent Detection
- [ ] Service inquiry detected correctly
- [ ] Complaints detected correctly
- [ ] Training inquiries detected correctly
- [ ] Confidence scoring works

### Routing
- [ ] Service → Sales department
- [ ] Complaint → Complaints department
- [ ] Training → Sales department
- [ ] Fallback to Reception for unknown

### Personas
- [ ] Reception persona displays correctly
- [ ] Sales persona displays correctly
- [ ] Complaints persona displays correctly
- [ ] Persona details include tone and expertise

### Ornina Data
- [ ] All 6 services available
- [ ] All 6 training programs available
- [ ] Contact information correct
- [ ] Company name: أورنينا (Ornina)
- [ ] Address: سوريا - دمشق - المزرعة
- [ ] Phone: 3349028

### Languages
- [ ] Arabic prompts load
- [ ] English prompts load
- [ ] Bilingual routing works
- [ ] Language auto-detection works

### Database
- [ ] Supabase connection successful
- [ ] Calls saved to database
- [ ] Transcripts saved
- [ ] Tickets created for complaints

### WebSocket
- [ ] WebSocket connection established
- [ ] Real-time routing updates sent
- [ ] Connection auto-reconnect works
- [ ] Graceful disconnect handling

---

## Next Steps After Testing

1. **If All Tests Pass** ✅
   - Run `git add callCenter/.env`
   - Create commit with environment setup
   - Push to GitHub
   - Deploy to production

2. **If Issues Found** ⚠️
   - Check logs for errors
   - Verify Supabase credentials
   - Test individual components in isolation
   - Fix issues and re-run tests

3. **Performance Testing**
   - Load test with multiple concurrent calls
   - Measure routing decision latency
   - Check database query performance
   - Monitor memory usage

---

## Success Indicators

✅ **Success looks like**:
- Backend runs without errors
- All three routing paths work
- Intent detection accurate
- Personas display with correct tone
- Supabase integration functional
- Bilingual support working
- WebSocket updates real-time
- Company data matches Avatar system

---

**Status**: Ready for Testing
**Date**: November 8, 2025
**Next**: Run tests and validate all scenarios
