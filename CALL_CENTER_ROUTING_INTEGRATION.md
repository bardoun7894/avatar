# Call Center Routing Integration Guide

**Date**: November 8, 2025
**Version**: 1.0
**Status**: Ready for Testing

---

## Overview

The Call Center system now uses the same Ornina company knowledge base as the Avatar system with intelligent intent-based routing:

- **Reception** → Collects customer info, detects intent
- **Sales** → Handles service inquiries and training questions
- **Complaints** → Handles customer issues and creates support tickets

All routing uses **Pydantic models** with bilingual (Arabic/English) support.

---

## Architecture

### Three Department Workflow

```
Customer Calls
    ↓
RECEPTION (Arabic/English greeting + data collection)
├─ Welcome: شركة أورنينا - أهلاً بك!
├─ Collect: Name, Phone, Email
├─ Ask: كيف بقدر ساعدك اليوم؟ (What do you need?)
├─ Detect Intent: complaint? service? training? info only?
    ↓
Route to Department:
├─ SALES (عرض الخدمات) → Service/Training inquiries
├─ COMPLAINTS (معالجة الشكاوى) → Customer problems
└─ INFORMATION → General info requests
```

### New Files Created

**`/var/www/avatar /callCenter/prompts/routing_prompts.py`** (400+ lines)
- **Pydantic Models**:
  - `CustomerInfo`: Collected customer data (name, phone, email, company, language)
  - `IntentDetection`: Detected intent with confidence and keywords
  - `RoutingDecision`: Final routing with all metadata
  - `DepartmentEnum`: RECEPTION, SALES, COMPLAINTS
  - `IntentEnum`: INQUIRY, SERVICE_INQUIRY, TRAINING_INQUIRY, COMPLAINT, etc.

- **Department Prompts** (Bilingual AR/EN):
  - `ReceptionPrompts`: Greeting, data collection, routing messages
  - `SalesPrompts`: Service explanations, budget/timeline questions
  - `ComplaintsPrompts`: Issue handling, ticket creation

- **Intent Detection**:
  - `IntentDetectionRules`: Keyword matching for each intent
  - `route_by_intent()`: Maps intent → department

### Updated Files

**`/var/www/avatar /callCenter/config.py`** (176 lines expanded)
- Added `COMPANY_NAME`, `COMPANY_NAME_FULL` (Ornina)
- Added `COMPANY_ADDRESS`, `COMPANY_PHONE`, `COMPANY_SOCIAL_MEDIA`
- Added `COMPANY_SERVICES` (6 services from Avatar):
  - AI Call Center
  - Film Production
  - AI Smart Ads
  - 2D/3D Animation
  - Digital Platform
  - Website Design & Development
- Added `COMPANY_TRAINING_PROGRAMS` (6 programs from Avatar):
  - Digital Marketing (45h)
  - Film Production (30h)
  - UI/UX Design (30h)
  - Coding Fundamentals (30h)
  - Fashion Design (10h)
  - Web Design (30h)

**`/var/www/avatar /callCenter/call_router.py`** (Enhanced)
- Added imports: `ReceptionPrompts`, `SalesPrompts`, `ComplaintsPrompts`
- New methods:
  - `detect_intent_from_message()`: Detect customer intent
  - `route_by_detected_intent()`: Route based on intent
  - `get_intent_routing_decision()`: Create full routing decision (Pydantic)
  - `get_department_greeting()`: Get department-specific greeting
  - `get_reception_prompt()`, `get_sales_prompt()`, `get_complaints_prompt()`

---

## Usage Examples

### 1. Basic Intent Detection

```python
from callCenter.call_router import get_call_router
from callCenter.prompts.routing_prompts import CustomerInfo

router = get_call_router()

# Example 1: Service Inquiry (Route to SALES)
customer_message = "أنا مهتم بخدمة الإعلانات الذكية"
intent = router.detect_intent_from_message(customer_message, language="ar")
print(intent)  # IntentEnum.SERVICE_INQUIRY

department = router.route_by_detected_intent(intent)
print(department)  # DepartmentEnum.SALES

# Example 2: Complaint (Route to COMPLAINTS)
customer_message = "عندي مشكلة مع طلبي السابق"
intent = router.detect_intent_from_message(customer_message, language="ar")
print(intent)  # IntentEnum.COMPLAINT

department = router.route_by_detected_intent(intent)
print(department)  # DepartmentEnum.COMPLAINTS

# Example 3: Training Inquiry (Route to SALES)
customer_message = "أريد معلومات عن دورات التدريب"
intent = router.detect_intent_from_message(customer_message, language="ar")
print(intent)  # IntentEnum.TRAINING_INQUIRY

department = router.route_by_detected_intent(intent)
print(department)  # DepartmentEnum.SALES
```

### 2. Complete Routing Decision (with Pydantic)

```python
# Create customer info
customer_info = CustomerInfo(
    name="علي محمد",
    phone="+966501234567",
    email="ali@example.com",
    company="شركة الرياض",
    language="ar"
)

# Get full routing decision
routing = router.get_intent_routing_decision(
    call_id="CALL-20251108-001",
    message="أنا أبحث عن خدمة تصميم موقع ويب احترافي",
    customer_info=customer_info,
    language="ar"
)

print(routing.intent_detection.intent)  # IntentEnum.SERVICE_INQUIRY
print(routing.intent_detection.department)  # DepartmentEnum.SALES
print(routing.intent_detection.confidence)  # 0.95
print(routing.intent_detection.reasoning)  # "Detected service_inquiry from customer message - routing to sales"

# Access as Pydantic model - type-safe!
assert routing.customer_info.name == "علي محمد"
```

### 3. Getting Department Prompts

```python
# Reception greeting
reception_greeting = router.get_reception_prompt("greeting", language="ar")
print(reception_greeting)
# السلام عليكم! أهلاً بك في شركة أورنينا للذكاء الاصطناعي والحلول الرقمية. كيف بقدر ساعدك اليوم؟

# Ask for name
name_prompt = router.get_reception_prompt("ask_name", language="ar")
print(name_prompt)
# من فضلك، ما اسمك الكامل؟

# Sales service explanation
sales_prompt = router.get_sales_prompt("service_ai_call_center", language="ar")
print(sales_prompt)
# نظام ذكي للرد التلقائي على العملاء 24/7...

# Complaints welcome
complaints_welcome = router.get_complaints_prompt("welcome", language="ar")
print(complaints_welcome)
# السلام عليكم! أنا من قسم معالجة الشكاوى. أنا هنا لمساعدتك.

# Use placeholders
routing_msg = router.get_sales_prompt(
    "create_opportunity",
    language="ar"
)
print(routing_msg)
# حسناً، سأنشئ لك فرصة عمل وسيتواصل معك الفريق قريباً لمناقشة التفاصيل.
```

### 4. Using with API (FastAPI example)

```python
from fastapi import FastAPI, WebSocket
from callCenter.call_router import get_call_router
from callCenter.prompts.routing_prompts import CustomerInfo

app = FastAPI()
router = get_call_router()

@app.post("/api/calls/{call_id}/detect-intent")
async def detect_intent_endpoint(call_id: str, message: str, language: str = "ar"):
    """Detect customer intent and route decision"""

    routing = router.get_intent_routing_decision(
        call_id=call_id,
        message=message,
        language=language
    )

    return {
        "call_id": routing.call_id,
        "intent": routing.intent_detection.intent.value,
        "department": routing.intent_detection.department.value,
        "confidence": routing.intent_detection.confidence,
        "routing_message": router.get_department_greeting(
            routing.intent_detection.department,
            language
        ),
        "keywords": routing.intent_detection.keywords,
        "reasoning": routing.intent_detection.reasoning
    }

@app.websocket("/ws/calls/{call_id}/routing")
async def websocket_routing_endpoint(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for real-time routing updates"""
    await websocket.accept()

    try:
        while True:
            # Receive customer message
            data = await websocket.receive_json()
            message = data.get("message", "")
            language = data.get("language", "ar")

            # Get routing decision
            routing = router.get_intent_routing_decision(
                call_id=call_id,
                message=message,
                language=language
            )

            # Send routing response
            await websocket.send_json({
                "intent": routing.intent_detection.intent.value,
                "department": routing.intent_detection.department.value,
                "greeting": router.get_department_greeting(
                    routing.intent_detection.department,
                    language
                ),
                "confidence": routing.intent_detection.confidence
            })
    except Exception as e:
        await websocket.send_json({"error": str(e)})
```

---

## Ornina Company Knowledge

### Services (Bilingual)

1. **Call Center بالذكاء الاصطناعي** (AI Call Center)
   - 24/7 Smart automatic response system
   - Bilingual Arabic/English support

2. **إنتاج الأفلام** (Film Production)
   - Professional visual content at low cost

3. **الإعلانات الذكية** (Smart Ads)
   - Platform-specific ads (TikTok, Instagram, YouTube)

4. **الأنيميشن 2D/3D** (Animation)
   - Professional animations for brands

5. **المنصة الرقمية** (Digital Platform)
   - One tool: videos, code, images, AI chat

6. **تصميم وبرمجة المواقع** (Web Design & Development)
   - Responsive, fast, secure websites

### Training Programs

1. **Digital Marketing** (45 hours)
2. **Film Production** (30 hours)
3. **UI/UX Design** (30 hours)
4. **Coding Fundamentals** (30 hours)
5. **Fashion Design** (10 hours)
6. **Web Design** (30 hours)

### Contact Information

- **Name**: أورنينا (Ornina)
- **Full Name**: شركة أورنينا للذكاء الاصطناعي والحلول الرقمية
- **Address**: سوريا - دمشق - المزرعة - مقابل وزارة التربية
- **Phone**: 3349028
- **Social Media**: @ornina.official (TikTok, Facebook, YouTube, Instagram)

---

## Pydantic Models Reference

### CustomerInfo

```python
from callCenter.prompts.routing_prompts import CustomerInfo, LanguageEnum

customer = CustomerInfo(
    name="أحمد علي",
    phone="+966501234567",
    email="ahmad@example.com",
    company="شركة النور",
    language=LanguageEnum.ARABIC  # or LanguageEnum.ENGLISH
)

# Access properties
print(customer.name)  # "أحمد علي"
print(customer.language.value)  # "ar"
```

### IntentDetection

```python
from callCenter.prompts.routing_prompts import IntentDetection, IntentEnum, DepartmentEnum

intent_result = IntentDetection(
    intent=IntentEnum.COMPLAINT,
    department=DepartmentEnum.COMPLAINTS,
    confidence=0.95,
    keywords=["مشكلة", "شكوى", "مشاكل"],
    reasoning="Customer mentioned complaint keywords"
)

# Access properties
print(intent_result.intent.value)  # "complaint"
print(intent_result.department.value)  # "complaints"
print(intent_result.confidence)  # 0.95
```

### RoutingDecision

```python
from callCenter.prompts.routing_prompts import RoutingDecision, CustomerInfo, IntentDetection

routing = RoutingDecision(
    call_id="CALL-20251108-001",
    customer_info=customer_info,
    intent_detection=intent_result,
    target_agent=None,
    timestamp="2025-11-08T10:30:00",
    metadata={"source": "web", "session_id": "sess-123"}
)

# Access nested properties
print(routing.customer_info.name)
print(routing.intent_detection.department)
print(routing.metadata.get("source"))
```

---

## Testing the Integration

### Test Scenario 1: Service Inquiry → Sales

```bash
# Customer: "أنا مهتم بخدمة الإعلانات"
# Expected: Route to SALES

curl -X POST "http://localhost:8000/api/calls/CALL-001/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "أنا مهتم بخدمة الإعلانات الذكية",
    "language": "ar"
  }'

# Response:
{
  "call_id": "CALL-001",
  "intent": "service_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم المبيعات...",
  "keywords": ["خدمة", "عندكم", ...],
  "reasoning": "Detected service_inquiry from customer message - routing to sales"
}
```

### Test Scenario 2: Complaint → Complaints

```bash
# Customer: "عندي مشكلة مع طلبي"
# Expected: Route to COMPLAINTS

curl -X POST "http://localhost:8000/api/calls/CALL-002/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "عندي مشكلة مع طلبي السابق، لم استقبل الخدمة",
    "language": "ar"
  }'

# Response:
{
  "call_id": "CALL-002",
  "intent": "complaint",
  "department": "complaints",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم معالجة الشكاوى...",
  "keywords": ["مشكلة", "شكوى", ...],
  "reasoning": "Detected complaint from customer message - routing to complaints"
}
```

### Test Scenario 3: Training Inquiry → Sales

```bash
# Customer: "أريد معلومات عن التدريبات"
# Expected: Route to SALES

curl -X POST "http://localhost:8000/api/calls/CALL-003/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "أريد معلومات عن برنامج التسويق الرقمي والتدريب",
    "language": "ar"
  }'

# Response:
{
  "call_id": "CALL-003",
  "intent": "training_inquiry",
  "department": "sales",
  "confidence": 0.95,
  "routing_message": "السلام عليكم! أنا من قسم المبيعات...",
  "keywords": ["تدريب", "دورة", ...],
  "reasoning": "Detected training_inquiry from customer message - routing to sales"
}
```

---

## Integration with Supabase

The Call Center uses the **same Supabase database** as Avatar:

```python
from callCenter.config import SUPABASE_URL, SUPABASE_KEY

# Same credentials as Avatar system
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-supabase-key"

# Same tables:
# - customers (customer profiles)
# - conversations (transcripts)
# - appointments (bookings)
# - call_logs (new - call center specific)
```

### Save Routing Decision to Supabase

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Save routing decision
await supabase.table("call_logs").insert({
    "call_id": routing.call_id,
    "customer_name": routing.customer_info.name,
    "customer_phone": routing.customer_info.phone,
    "customer_email": routing.customer_info.email,
    "detected_intent": routing.intent_detection.intent.value,
    "routed_department": routing.intent_detection.department.value,
    "confidence": routing.intent_detection.confidence,
    "language": routing.customer_info.language.value,
    "created_at": routing.timestamp,
    "metadata": routing.metadata
})
```

---

## Summary

✅ **Completed**:
- Ornina company info synced to Call Center config
- Pydantic models for routing with type safety
- Bilingual (Arabic/English) prompts for all departments
- Intent detection with keyword matching
- Intelligent routing: Reception → Sales/Complaints
- Integration with existing Supabase database

✅ **Ready to Use**:
- Import routing_prompts in your code
- Use `get_call_router()` for routing
- Call `get_intent_routing_decision()` for complete routing
- Access Pydantic models for type-safe operations

---

## Next Steps

1. **Integrate with API**: Add routing endpoints to `/var/www/avatar /callCenter/api.py`
2. **Test all scenarios**: Run manual tests from CALL_CENTER_TESTING_WORKFLOW.md
3. **Monitor WebSocket**: Check real-time routing updates
4. **Verify database**: Confirm routing decisions are saved to Supabase
5. **Deploy**: Start Call Center with `./start-call-center.sh`

---

**Status**: ✅ Ready for Integration Testing
**Date**: November 8, 2025
