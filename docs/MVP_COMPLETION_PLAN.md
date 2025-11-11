# MVP Completion Plan - Ornina AI Call Center

**Objective:** Activate core sentiment-based routing feature and complete MVP functionality
**Current Status:** 70% complete (infrastructure ready, core feature broken)
**Target Timeline:** 1 week (48-64 hours focused development)
**Success Criteria:** Full end-to-end multi-assistant call with sentiment-driven routing

---

## What's Blocking MVP

The system is **fully built except one critical integration**:

**The Problem:**
- Sentiment analysis code exists but is **never called**
- Persona switching logic is written but **never triggered**
- Result: Agent stays on "reception" persona regardless of customer input
- Impact: **Core value proposition (intelligent routing) is broken**

**Example of Current Broken Behavior:**
```
Customer: "This is amazing! I want to buy your product!"
System: Analyzes sentiment (POSITIVE/INTERESTED) ✓
System: Should route to Sales assistant ✓
System: Actually continues with Reception ✗
```

**What Should Happen:**
```
Customer: "This is amazing! I want to buy your product!"
System: Analyzes sentiment (POSITIVE/INTERESTED) ✓
System: Routes to Sarah (Sales) ✓
Sarah: "Great! I see you're interested in our product..."
Customer: "Yes, what are the pricing options?"
Sarah: "We have three tiers: Starter, Professional, Enterprise..."
```

---

## 7-Day Sprint Plan

### **Day 1-2: Sentiment Routing Integration (16 hours)**

#### Task 1.1: Wire Sentiment Analysis into Agent Loop (6 hours)

**File:** `/var/www/avatar/callCenter/call_center_agent.py`

**Current Code (Broken):**
```python
class CallCenterAgent(VoiceAssistant):
    async def handle_message(self, message: str):
        # Agent processes message with current persona
        response = await self.llm.generate(
            system_prompt=self.current_persona_prompt,
            user_message=message
        )
        return response
```

**Required Changes:**
```python
class CallCenterAgent(VoiceAssistant):
    async def handle_message(self, message: str):
        # NEW: Analyze sentiment of customer message
        sentiment = analyze_sentiment(message)

        # NEW: Determine if we should switch assistants
        recommended_assistant = determine_appropriate_assistant(
            sentiment=sentiment,
            conversation_context=self.conversation_history
        )

        # NEW: Switch if needed
        if recommended_assistant != self.current_assistant:
            await self.switch_persona(recommended_assistant)

        # EXISTING: Generate response with current (possibly new) persona
        response = await self.llm.generate(
            system_prompt=self.current_persona_prompt,
            user_message=message
        )
        return response
```

**Steps:**
1. Import sentiment analysis functions
2. Add sentiment extraction after each customer message
3. Call routing logic to determine best assistant
4. Trigger persona switch if needed
5. Add logging for debugging

**Testing:**
```bash
# Test with positive sentiment
agent.handle_message("This is fantastic! I want to buy!")
# Should switch to Sales (Sarah)

# Test with negative sentiment
agent.handle_message("Your service is terrible, I'm frustrated")
# Should switch to Support (Mohammed)

# Test with neutral
agent.handle_message("What's your product?"
# Should stay with Reception (Ahmed)
```

---

#### Task 1.2: Implement Persona Switching Logic (5 hours)

**File:** `/var/www/avatar/callCenter/conversation_manager.py`

**Current Code (Incomplete):**
```python
def determine_appropriate_assistant(sentiment: dict) -> str:
    """Returns assistant name but never actually switches"""
    if sentiment.get('class') == 'POSITIVE':
        return 'sales'
    elif sentiment.get('class') == 'NEGATIVE':
        return 'complaints'
    else:
        return 'reception'
```

**Required Changes:**
```python
class ConversationManager:
    async def switch_persona(self, new_assistant: str):
        """Actually switches the active persona"""
        old_assistant = self.current_assistant

        # Load new persona
        new_persona = self.personas.get(new_assistant)

        # Inject context about previous conversation
        context = self._prepare_context_for_switch(
            from_assistant=old_assistant,
            to_assistant=new_assistant
        )

        # Update system prompt with context
        system_prompt = new_persona.get_prompt_with_context(context)

        # Update agent's system prompt
        self.current_system_prompt = system_prompt
        self.current_assistant = new_assistant

        # Generate transition message for customer
        transition = await self.llm.generate(
            system_prompt=system_prompt,
            user_message="[SYSTEM: You were just switched by the routing system]"
        )

        return transition
```

**Steps:**
1. Implement `switch_persona()` method
2. Load new persona configuration
3. Inject conversation context
4. Generate natural transition message
5. Update agent state

**Testing:**
```python
# Test persona switch
await manager.switch_persona('sales')
assert manager.current_assistant == 'sales'
assert 'sales' in manager.current_system_prompt
```

---

#### Task 1.3: Wire Context Through Persona Transitions (5 hours)

**File:** `/var/www/avatar/callCenter/openai_personas.py`

**Required Changes:**
```python
class Persona:
    def get_prompt_with_context(self, context: dict) -> str:
        """Injects customer context into persona prompt"""
        customer_context = f"""
        Previous conversation with {context['previous_assistant']}:
        {context['previous_messages'][-3:]}  # Last 3 messages

        Customer profile:
        - Name: {context['customer_name']}
        - Purchase history: {context['purchase_history']}
        - VIP: {context['is_vip']}
        """

        return self.base_prompt + "\n\n" + customer_context
```

**Steps:**
1. Enhance persona prompts to include context injection
2. Prepare customer history on switch
3. Include previous conversation snippets
4. Add acknowledgment lines: "I see you were interested in..."

---

### **Day 3: Testing & Validation (16 hours)**

#### Task 3.1: Unit Tests for Sentiment Analysis (4 hours)

**File:** `/var/www/avatar/callCenter/test_sentiment.py`

```python
import pytest
from conversation_analyzer import analyze_sentiment
from conversation_manager import determine_appropriate_assistant

def test_positive_sentiment():
    result = analyze_sentiment("This is amazing! I love it!")
    assert result['class'] == 'POSITIVE'
    assert result['confidence'] > 0.85

def test_negative_sentiment():
    result = analyze_sentiment("Your service is terrible!")
    assert result['class'] == 'NEGATIVE'

def test_routing_logic():
    # Positive should route to sales
    assistant = determine_appropriate_assistant({'class': 'POSITIVE'})
    assert assistant == 'sales'

    # Negative should route to support
    assistant = determine_appropriate_assistant({'class': 'NEGATIVE'})
    assert assistant == 'complaints'
```

**Target:** 100% pass rate, >80% code coverage

---

#### Task 3.2: Integration Tests - Full Call Flow (6 hours)

**File:** `/var/www/avatar/callCenter/test_e2e_routing.py`

```python
@pytest.mark.asyncio
async def test_call_with_sentiment_routing():
    """End-to-end test: call starts with reception, routes to sales"""

    # Setup
    agent = CallCenterAgent()
    await agent.initialize()

    # Customer greets
    msg1 = "Hi, I'm calling about your product"
    response1 = await agent.handle_message(msg1)
    assert 'reception' in agent.current_system_prompt

    # Customer shows interest
    msg2 = "This sounds perfect! How much does it cost?"
    response2 = await agent.handle_message(msg2)

    # Verify routing to sales
    assert 'sales' in agent.current_system_prompt or agent.current_assistant == 'sarah'
    assert "pricing" in response2.lower()
```

**Success Criteria:**
- ✅ Call starts with reception
- ✅ Positive sentiment triggers routing
- ✅ Response includes sales-appropriate language
- ✅ Context from previous messages included

---

#### Task 3.3: Load Testing (3 hours)

```python
# Test simultaneous calls with routing
# Verify system handles 10+ concurrent calls with sentiment routing
# Measure latency of routing decision (<500ms)
```

---

#### Task 3.4: Manual QA Testing (3 hours)

**Test Scenarios:**
1. **Happy Path - Sales Route**
   - Call with positive/interested sentiment
   - Verify transition to Sales assistant
   - Confirm pricing/product discussion

2. **Support Route**
   - Call with complaints/negative sentiment
   - Verify transition to Support assistant
   - Confirm issue resolution focus

3. **Reception Route**
   - Call with neutral sentiment
   - Stay with reception for information gathering
   - Natural escalation to sales/support

4. **Mixed Sentiment**
   - Start negative, become positive
   - Verify re-routing logic
   - Test context preservation

---

### **Day 4-5: Feature Completion (16 hours)**

#### Task 4.1: Activate ElevenLabs TTS (3 hours)

**Current Issue:** TTS configured but not active in agent loop

**File:** `/var/www/avatar/callCenter/call_center_agent.py`

```python
async def synthesize_response(self, text: str) -> bytes:
    """Convert text response to audio"""
    audio = await elevenlabs_client.synthesize(
        text=text,
        voice_id=self.current_persona.voice_id,
        language='ar'  # Arabic
    )
    return audio
```

**Steps:**
1. Verify ElevenLabs API key is configured
2. Test voice synthesis with sample text
3. Integrate into response pipeline
4. Test audio quality and latency

---

#### Task 4.2: Implement Call Recording (5 hours)

**File:** `/var/www/avatar/callCenter/livekit_manager.py`

```python
async def start_recording(self, call_id: str, room_name: str):
    """Record call to S3 with encryption"""
    recording = await self.livekit.start_recording(room_name)
    # Store recording metadata in database
    await self.db.recordings.insert({
        'call_id': call_id,
        'livekit_recording_id': recording.id,
        'status': 'recording',
        'start_time': datetime.now()
    })
```

**Steps:**
1. Enable LiveKit recording
2. Configure S3 storage
3. Encrypt recordings at rest
4. Store metadata in database

---

#### Task 4.3: Build Analytics Pipeline (8 hours)

**Create:** `/var/www/avatar/callCenter/analytics_collector.py`

```python
class AnalyticsCollector:
    async def record_call_completed(self, call_data: dict):
        """Collect metrics from completed call"""
        metrics = {
            'call_id': call_data['id'],
            'duration': call_data['end_time'] - call_data['start_time'],
            'assistants_used': call_data['assistant_sequence'],
            'routing_count': len(call_data['assistant_sequence']),
            'final_sentiment': call_data['final_sentiment'],
            'customer_satisfaction': call_data.get('satisfaction_score'),
            'timestamp': datetime.now()
        }

        # Store in analytics table
        await self.db.call_analytics.insert(metrics)

        # Update aggregates for dashboard
        await self.update_dashboard_metrics(metrics)
```

**Steps:**
1. Collect metrics from each call
2. Store in analytics table
3. Create aggregation jobs (hourly/daily)
4. Implement dashboard queries

---

### **Day 6-7: Documentation & Polish (16 hours)**

#### Task 6.1: Update Documentation (5 hours)
- Update API documentation with routing details
- Add troubleshooting guide
- Create deployment checklist

#### Task 6.2: Create Runbooks (3 hours)
- Incident response procedures
- Common issues and fixes
- Monitoring and alerting setup

#### Task 6.3: Final Testing & QA (5 hours)
- Complete regression testing
- Verify all features work
- Document any known issues

#### Task 6.4: Staging Deployment (3 hours)
- Deploy to staging environment
- Final validation
- Prepare for production

---

## Success Criteria for MVP

### Functional Requirements ✅
- ✅ Audio calls work end-to-end
- ✅ Sentiment analysis runs in real-time
- ✅ **NEW:** Persona switches based on sentiment
- ✅ Context is preserved through transitions
- ✅ Calls are recorded and transcribed
- ✅ Customer profiles are accessible
- ✅ API endpoints return correct data

### Performance Requirements
- ✅ Response latency <3 seconds (full cycle)
- ✅ Sentiment analysis <500ms
- ✅ Persona switch <2 seconds
- ✅ Handle 10+ concurrent calls

### Quality Requirements
- ✅ Test coverage >60%
- ✅ All unit tests passing
- ✅ E2E tests for happy path
- ✅ No critical bugs

### Deployment Requirements
- ✅ Docker images build
- ✅ Environment variables configured
- ✅ Database migrations run
- ✅ Services start cleanly

---

## Daily Standup Template

```
Day X: [Task Summary]

✅ Completed:
- [Item]
- [Item]

⏳ In Progress:
- [Item]
- [Item]

🚫 Blockers:
- [Issue]

📊 Metrics:
- Tests passing: X/Y
- Code coverage: X%
- Lines of code added: X
```

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Sentiment API failures | Medium | Implement fallback (default to reception) |
| Persona switch breaks context | Medium | Extensive testing of context injection |
| Performance degradation | Low | Load testing before day 5 |
| Integration issues | Low | Daily integration testing |

---

## Definition of Done

Each story is complete when:
1. ✅ Code written and committed
2. ✅ Unit tests passing (>80% coverage)
3. ✅ Integration tests passing
4. ✅ Peer reviewed
5. ✅ Documentation updated
6. ✅ Deployed to staging
7. ✅ Manual QA passed

---

## Resources Needed

**Tools:**
- Python 3.11+ environment
- Docker & Docker Compose
- Git for version control
- Python testing frameworks (pytest)
- API testing tool (Postman/curl)

**Access:**
- Supabase database
- OpenAI API key
- ElevenLabs API key
- LiveKit project

**Time:**
- 1-2 developers
- 48-64 focused hours
- 1 week calendar time

---

## Next Action

**Start immediately with Day 1-2:**
1. Review current sentiment analysis code
2. Modify call_center_agent.py to call sentiment analysis
3. Implement persona switching in conversation_manager.py
4. Test with manual call scenarios

**Expected outcome by end of Day 2:**
- Sentiment analysis runs during calls
- Persona switches based on sentiment
- Basic routing working
- Ready for comprehensive testing

---

**Created:** 2025-11-10
**Target Completion:** 2025-11-17
**Status:** Ready to start development
