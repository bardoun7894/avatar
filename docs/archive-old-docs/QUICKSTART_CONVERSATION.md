# 🚀 Quick Start - Call Center Conversations

**Get conversations running in 5 minutes!**

---

## ⚡ Quick Start (5 minutes)

### 1. Start the Backend
```bash
cd "/var/www/avatar /callCenter"
source venv/bin/activate
python3 main.py
```

Expected output:
```
Starting Call Center API Server...
Server will be available at http://localhost:8000
Initialized 3 agents
```

### 2. Run Test Script
```bash
# In another terminal
cd "/var/www/avatar /callCenter"
source venv/bin/activate
python3 test_conversation.py
```

This will run 5 complete conversation scenarios demonstrating:
- ✅ Service inquiries (Reception → Sales)
- ✅ Complaint handling (Reception → Complaints)
- ✅ Full conversation flow
- ✅ Persona manager
- ✅ Manual persona switching

### 3. Test via API
```bash
# Send a message
curl -X POST "https://184.174.37.148/api/conversations/CALL-001/message" \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "message": "I am interested in your advertising service",
    "language": "en"
  }'
```

### 4. Test via WebSocket
```bash
# Connect to WebSocket
wscat -c wss://184.174.37.148/api/conversations/ws/CALL-001

# Send message in WebSocket
{"message": "Hello, how can you help me?", "language": "en"}
```

---

## 📱 Sample Conversation Flow

### Customer initiates call
```
Reception Agent: "Hello! Welcome to Ornina. I'm Ahmed from our reception team. How can I help you today?"
```

### Customer asks about service
```
Customer: "I'm interested in your digital platform service"

→ System detects: SERVICE_INQUIRY + SALES_INTEREST
→ Routes to: SALES (Sarah)
```

### Sales takes over
```
Sales Agent: "Excellent! That's one of our most popular services. Let me tell you more about it."
```

### Customer asks pricing
```
Customer: "What's the pricing?"

→ System detects: SALES_INTEREST
→ Routes to: Continue with SALES
```

### Sales closes conversation
```
Sales Agent: "I'd love to discuss this further and create a custom proposal for you. Can I get your contact information?"
```

---

## 🎯 Key Features Demonstrated

### ✅ Real-time Responses
- OpenAI generates unique responses
- Each persona has distinct voice
- Context-aware replies

### ✅ Smart Routing
- Automatic persona detection
- Switches based on intent
- Considers sentiment
- Escalates when needed

### ✅ Bilingual Support
- Arabic & English
- Auto language detection
- Persona names in both languages

### ✅ Conversation Analysis
- Intent detection
- Sentiment analysis
- Priority scoring
- Ticket creation

---

## 📊 What Happens Behind the Scenes

```
Customer Message
    ↓
Conversation Analyzer (Pydantic)
    ├─ Detect Intent
    ├─ Analyze Sentiment
    ├─ Generate Routing Decision
    └─ Validate with Pydantic models
    ↓
Route to Correct Persona
    ├─ Reception: Greeting & Info
    ├─ Sales: Services & Pricing
    └─ Complaints: Issues & Tickets
    ↓
OpenAI Generation
    ├─ System prompt from persona
    ├─ Conversation history
    └─ Generate contextual response
    ↓
Save to Conversation State
    ├─ Add to transcript
    ├─ Update statistics
    └─ Log analysis results
    ↓
Send to Customer
    ├─ Real-time (WebSocket)
    └─ Or REST response
```

---

## 🔍 Example: Complaint Handling

**Customer**: "My service isn't working, I'm really frustrated"

**Step 1: Analysis**
```
Intent: TECHNICAL_SUPPORT (complaint keywords detected)
Sentiment: NEGATIVE → FRUSTRATED (emotion indicators)
Priority: HIGH (complaint + frustrated)
```

**Step 2: Routing Decision**
```
Target Persona: COMPLAINTS (Mohammed)
Priority: HIGH
Create Ticket: YES
Escalation: YES (customer is frustrated)
```

**Step 3: Route**
```
→ Switch from Reception to Complaints
→ Mohammed (empathetic tone) takes over
```

**Step 4: Response**
```
Mohammed: "I'm very sorry to hear that. I completely understand your frustration.
Let me get this documented right away so we can resolve it for you."
```

**Step 5: Action**
```
→ Create HIGH priority ticket
→ Assign to support team
→ Schedule follow-up
```

---

## 🗣️ 3 Personas Explained

### 👨 Reception (Ahmed)
- **Tone**: Friendly, helpful
- **Role**: Initial greeting, information
- **Expertise**: Company services, routing
- **Response Style**: Warm and professional
- **Languages**: Arabic & English

### 👩 Sales (Sarah)
- **Tone**: Enthusiastic, persuasive
- **Role**: Service explanation, offers
- **Expertise**: Products, pricing, deals
- **Response Style**: Exciting and solution-focused
- **Languages**: Arabic & English

### 👨‍💼 Complaints (Mohammed)
- **Tone**: Empathetic, professional
- **Role**: Issue resolution, support
- **Expertise**: Problem-solving, tickets
- **Response Style**: Caring and action-focused
- **Languages**: Arabic & English

---

## 📝 Test Scenarios Included

### Test 1: Service Inquiry
- Customer asks about advertising service
- Routes from Reception → Sales
- Tests automatic persona switching

### Test 2: Complaint Handling
- Customer has a problem
- Routes from Reception → Complaints
- Tests ticket auto-creation

### Test 3: Full Flow (English)
- Complete 3-message conversation
- All in English
- Tests full conversation lifecycle

### Test 4: Persona Manager
- Lists all 3 personas
- Shows attributes
- Demonstrates persona information

### Test 5: Manual Switching
- Tests switching between personas manually
- Shows different responses

---

## 🎓 Example Intents Detected

| Intent | Keywords | Routes To |
|--------|----------|-----------|
| Complaint | problem, issue, broken, error | Complaints |
| Sales | price, interested, offer, buy | Sales |
| Service Info | information, tell me, about | Reception |
| Training | course, learning, program | Sales |
| Technical | bug, crash, not working | Complaints |
| Billing | invoice, payment, charge | Complaints |

---

## 🌍 Language Support

### Arabic (ar)
- Auto-detects Arabic text
- Persona names in Arabic
- Responses in Arabic
- Keywords in Arabic

### English (en)
- Auto-detects English text
- Persona names in English
- Responses in English
- Keywords in English

**Usage**:
```python
# Specify language
manager = get_conversation_manager(call_id, customer_name, language="ar")
```

---

## 📊 Statistics Generated

Each conversation tracks:
- ✅ Total messages
- ✅ User vs Assistant messages
- ✅ Personas used
- ✅ Intents detected
- ✅ Sentiment progression
- ✅ Escalations
- ✅ Duration
- ✅ Satisfaction level

---

## 🐛 Troubleshooting

### OpenAI Not Responding?
- Mock responses still work (for testing)
- Check OPENAI_API_KEY in `.env`
- Verify API key is valid

### Wrong Persona Detected?
- Check confidence score
- Low confidence defaults to Reception
- Manually switch if needed: `/api/conversations/{id}/switch-persona`

### Connection Issues?
- WebSocket: Try REST API alternative
- REST: Check HTTPS certificate (use -k flag)
- Backend: Check logs at `/tmp/callcenter.log`

---

## ✅ Success Checklist

- [ ] Backend running (`python3 main.py`)
- [ ] Test script runs successfully
- [ ] Can send API messages
- [ ] Can connect WebSocket
- [ ] Get responses from OpenAI (or mock)
- [ ] Personas switch automatically
- [ ] Arabic & English both work
- [ ] Transcripts are saved

---

## 🚀 Next Steps

1. ✅ Run test script
2. ✅ Test API endpoints
3. ✅ Connect WebSocket
4. 📝 Test with real calls
5. 🔗 Connect Supabase DB
6. 📊 Monitor conversations
7. 🚀 Deploy to production

---

## 📞 API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/conversations/{id}/message` | POST | Send message |
| `/api/conversations/{id}/transcript` | GET | Get transcript |
| `/api/conversations/{id}/stats` | GET | Get statistics |
| `/api/conversations/ws/{id}` | WS | Real-time stream |
| `/api/conversations/{id}/switch-persona` | POST | Switch persona |

---

## 🎉 You're Ready!

Run this to get started:
```bash
cd "/var/www/avatar /callCenter"
source venv/bin/activate
python3 test_conversation.py
```

Watch the complete conversation system in action with all 3 personas! 🎬

---

**Status**: ✅ **READY TO USE**
**Last Updated**: November 9, 2025

