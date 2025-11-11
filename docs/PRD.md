# Ornina AI Call Center - Product Requirements Document

**Author:** mohamed
**Date:** 2025-11-10
**Version:** 1.0
**Status:** Active Development

---

## Executive Summary

**Ornina AI Call Center** is a 24/7 intelligent multi-assistant audio communication system designed for Arabic-speaking businesses across the Middle East and North Africa (MENA). The platform combines sophisticated Arabic language processing (Syrian dialect) with multi-assistant routing, delivering cost-effective customer service automation without video overhead.

The system intelligently routes conversations between three specialized AI personas (Reception, Sales, Support) based on real-time sentiment analysis, ensuring customers always reach the right assistant for their needs.

### What Makes This Special ✨

**The Magic:** Seamless, culturally-aware Arabic conversations that feel natural—customers don't realize they're talking to AI. The system understands Syrian dialect nuances, maintains context across assistant transitions, and provides 24/7 intelligent support that scales without hiring costs.

**Key Differentiators:**
- 🎯 **Native Arabic Intelligence** - Syrian dialect fluency, not just translation
- 🔄 **Smart Transitions** - Sentiment-driven routing feels like a natural handoff
- ⚡ **24/7 Availability** - Always-on support, dramatically lower operational costs
- 💬 **Multi-Persona System** - Three specialized AI personalities, each optimized for their role
- 📊 **Context Awareness** - Remembers conversation history and customer context

---

## Project Classification

**Technical Type:** SaaS B2B Platform + API Backend + Audio AI Agent System
**Domain:** Customer Service Automation, AI/ML, Conversational Systems
**Complexity:** Medium-High (Multi-assistant routing, Arabic NLU, real-time sentiment analysis)

**Project Scope:** Standalone Audio Call Center Application
- **Separate from:** Avatar video system (different app, different deployment)
- **Focus:** Audio-only, cost-optimized, high-volume customer interactions
- **Architecture:** Microservices (FastAPI + LiveKit Agents + OpenAI + Sentiment Analysis)

### Domain Context

**Target Markets:** Syria, Lebanon, UAE, Saudi Arabia, Egypt, Jordan
**Industry Verticals:** E-commerce, Hospitality, Banking, Telecom, Healthcare, Government Services

**Regional Considerations:**
- Arabic dialect diversity (Syrian focus, but scalable to other Gulf/Levantine dialects)
- Data residency and compliance requirements by country
- Cultural nuances in customer service expectations
- Peak usage patterns in MENA region

---

## Success Criteria

**We succeed when:**

1. **Customer Experience (Primary)**
   - Customers have natural, seamless conversations in Arabic (Syrian dialect)
   - Transitions between assistants happen smoothly without customer confusion
   - Average resolution time < 5 minutes for common queries
   - Customer satisfaction score > 4.2/5.0

2. **Operational Metrics**
   - System availability: 99.5% uptime (24/7 operation)
   - Concurrent calls: Handle 100+ simultaneous conversations
   - Cost per call: < $0.05 (vs. $2-5 for human agents)
   - Sentiment routing accuracy: > 85%

3. **Business Impact**
   - Reduce customer support costs by 70-80%
   - Handle 10,000+ calls/day without scaling headcount
   - Customer retention rate improvement of 15%+
   - Enterprise customer acquisition: 10+ paying customers in first 6 months

4. **Product Quality**
   - Speech recognition accuracy: > 90% for Arabic/Syrian dialect
   - Zero data loss during calls
   - Call recording and analytics working seamlessly
   - System handles graceful error recovery without customer notice

### Business Metrics

- **Revenue Model:** Per-call pricing ($0.015-0.05) + Monthly platform subscription ($500-5000)
- **Target CAC:** < $2,000 per enterprise customer
- **Target LTV:** > $50,000 per customer
- **Break-even:** 6-8 months after first customer acquisition

---

## Product Scope

### MVP - Minimum Viable Product (Phase 1 - NOW)

**Core Functionality:**
- [x] Audio-only call center (no video)
- [x] Three AI personas: Ahmed (Reception), Sarah (Sales), Mohammed (Support)
- [x] Arabic language support (Syrian dialect)
- [x] Sentiment-based routing between assistants
- [x] Call recording and logs
- [x] Basic CRM integration
- [x] Web dashboard for call history
- [x] API for token generation and call management

**Technical Stack:**
- FastAPI backend (Call Center API)
- LiveKit for audio infrastructure
- OpenAI GPT-4 Turbo (LLM)
- ElevenLabs (Arabic TTS)
- Supabase PostgreSQL (storage + CRM data)
- Next.js frontend dashboard

**Success Metric:** 5+ paying customers, handling 500+ calls/day, >85% sentiment routing accuracy

### Growth Features (Post-MVP)

**Phase 2 - Enhanced Intelligence (3-4 months after MVP):**
- Multi-dialect support (Lebanese, Gulf, Egyptian Arabic)
- Advanced sentiment analysis with emotion detection (anger, frustration, happiness)
- CRM context injection (customer history, purchase records, preferences)
- Custom assistant personas per enterprise (branded voices, tone)
- Analytics dashboard (call duration, sentiment trends, routing statistics)
- Call transfer to human agents with context preservation
- Escalation workflows for complex issues

**Phase 3 - Enterprise Features (6-8 months after MVP):**
- Multi-language support beyond Arabic
- Custom training data per customer (company-specific knowledge)
- Quality assurance module (human review of sensitive calls)
- Compliance reporting (GDPR, local data protection laws)
- Advanced CRM integrations (Salesforce, HubSpot, custom systems)
- A/B testing framework for assistant personas
- Real-time monitoring and alerts

**Phase 4 - AI Advancement (9-12 months):**
- Fine-tuned Arabic language models (not just GPT-4)
- Contextual understanding across multiple customer interactions
- Predictive assistance (suggests next action to human agents)
- Conversation summarization (automatic ticket creation)
- Multimodal support (email, WhatsApp, Telegram alongside calls)

### Vision (Future - Year 2+)

- **Full Omnichannel:** Unified AI assistant across voice, chat, email, social media
- **Human-in-the-Loop:** Seamless escalation and collaboration with human teams
- **Industry-Specific Solutions:** Pre-built templates for banking, healthcare, e-commerce
- **Global Expansion:** Support for all major world languages
- **Advanced Analytics:** Predictive customer churn, sentiment trends, operational insights

---

## Domain-Specific Requirements

**Customer Service Automation Domain Considerations:**

1. **Data Privacy & Compliance**
   - GDPR compliance for EU-based customers
   - Local data residency requirements (Syria, UAE, etc.)
   - Call recording and consent management
   - Right to be forgotten implementations
   - Regular security audits

2. **Quality & Accuracy Standards**
   - Speech recognition accuracy > 90% for Arabic dialects
   - Intent understanding accuracy > 85%
   - Sentiment analysis precision > 85%
   - Zero tolerance for discriminatory or offensive responses

3. **Operational Reliability**
   - 99.5% uptime SLA for paid customers
   - Automatic failover for agent disconnects
   - Call quality monitoring (no dropped audio, latency < 200ms)
   - Automatic logging and debugging

4. **Cultural & Regional Considerations**
   - Respect for business hours and holidays by region
   - Culturally appropriate responses and tone
   - Support for local payment methods
   - Regional variation in service expectations

---

## Innovation & Novel Patterns

**AI-Driven Multi-Assistant Routing:**

The innovation here is combining:
1. **Real-time Sentiment Analysis** - Analyzing customer emotion as they speak
2. **Dynamic Assistant Selection** - Automatically routing to the best-suited AI persona
3. **Context Preservation** - Maintaining conversation history across handoffs
4. **Natural Transitions** - Making handoffs feel like talking to departments, not systems

**This differs from existing solutions:**
- Most use keyword routing (if customer says "sales", route to sales)
- We use sentiment + context (customer seems interested → sales assistant)
- Most lose context on handoff
- We maintain full conversation history

### Validation Approach

- **Sentiment Routing Accuracy:** Test with 100+ recorded conversations, measure routing vs. ideal
- **Customer Satisfaction:** NPS surveys after calls
- **Agent Quality:** Human review of sample conversations from each persona
- **Dialect Handling:** Test with native speakers from different regions

---

## API Backend & SaaS Specific Requirements

### Multi-Tenant Architecture

**Isolation Model:**
- **Data Isolation:** Each customer has isolated call logs, conversations, and CRM data
- **API Token Isolation:** Unique tokens per customer, scoped permissions
- **Resource Allocation:** Separate concurrent call limits per customer tier
- **Billing Isolation:** Per-customer usage tracking and invoicing

**Tenant Tiers:**
1. **Starter:** Up to 50 calls/day, 1 assistant persona, basic analytics
2. **Professional:** Up to 500 calls/day, 3 custom personas, advanced analytics
3. **Enterprise:** Unlimited calls, unlimited personas, dedicated support, custom integrations

### API Specification

**Core Endpoints:**

1. **Authentication**
   ```
   POST /api/auth/token
   - Input: API key + secret
   - Output: JWT token (1-hour expiry)
   ```

2. **Call Management**
   ```
   POST /api/calls/initiate
   - Input: customer_phone, assistant_type (reception/sales/support)
   - Output: room_token, livekit_url

   GET /api/calls/{call_id}
   - Output: call_status, duration, transcript, sentiment_history

   GET /api/calls
   - Query: date_range, customer_id, sentiment_filter
   - Output: List of calls with metadata
   ```

3. **CRM Integration**
   ```
   POST /api/crm/customer
   - Input: customer_data (name, phone, purchase_history, preferences)
   - Output: customer_id

   GET /api/crm/customer/{phone}
   - Output: Customer profile with conversation history
   ```

4. **Analytics**
   ```
   GET /api/analytics/summary
   - Query: date_range
   - Output: Total calls, avg duration, sentiment distribution, routing accuracy

   GET /api/analytics/conversations
   - Output: Conversation trends, peak times, common issues
   ```

5. **Admin**
   ```
   POST /api/admin/assistant/update
   - Input: assistant_id, new_prompt, new_tone
   - Output: Updated assistant config

   GET /api/admin/usage
   - Output: Per-customer usage, billing summary
   ```

### Authentication & Authorization

**Token-Based Authentication:**
- Each customer gets an API key + secret
- Endpoints return JWT tokens (1-hour expiry)
- Token includes customer_id, scoped permissions
- Rate limiting: 10 requests/second per token

**Permission Matrix:**
- **customer_read:** View own calls and conversations
- **customer_write:** Initiate new calls
- **crm_read:** Access CRM data
- **crm_write:** Update customer profiles
- **analytics_read:** View usage and metrics
- **admin_write:** Modify assistant personas (enterprise only)

---

## Functional Requirements

### 1. Audio Call Center Core

**FR-1: Multi-Persona Assistant System**
- System must maintain 3 independent AI personas (Reception, Sales, Support)
- Each persona has distinct:
  - System prompt (instructions for behavior)
  - Voice characteristics (tone, speaking speed via ElevenLabs parameters)
  - Response patterns (warm vs. sales-focused vs. empathetic)
- Personas are swappable and updatable via API

**FR-2: Real-Time Sentiment Analysis**
- Analyze customer speech in real-time as they speak
- Classify sentiment into categories: Positive, Negative, Neutral, Interested, Complaining
- Route based on sentiment:
  - Positive/Interested → Sales Assistant
  - Negative/Complaining → Support Assistant
  - Neutral/Inquiry → Reception Assistant
- Sentiment confidence > 85%

**FR-3: Seamless Assistant Transitions**
- When routing decision made, transition to new assistant smoothly:
  - Pass full conversation context (previous messages)
  - New assistant acknowledges context: "I see you were interested in..."
  - No perceptible delay (< 2 seconds)
  - Customer feels they're talking to a department, not a different system

**FR-4: Arabic Language Support**
- Speech-to-Text: Recognize Syrian dialect with > 90% accuracy
- Language Model: Understand and respond in Arabic naturally
- Text-to-Speech: ElevenLabs Arabic voice, natural pronunciation
- Support fallback for Modern Standard Arabic (MSA)

**FR-5: Call Recording & Transcript**
- Record all calls automatically
- Generate transcript with timestamps
- Store securely with encryption
- Provide download link to customer (with consent)

**FR-6: Call History & Logging**
- Log all calls with metadata:
  - Participant (customer phone), duration, start/end time
  - Initial assistant and routing decisions
  - Sentiment values over time
  - Final resolution status
- Full audit trail for compliance

### 2. CRM & Customer Context

**FR-7: Customer Profile Management**
- Store customer information: Name, phone, email, address
- Track purchase/service history
- Store preferences and conversation tags
- Link multiple phone numbers to same customer

**FR-8: Context Injection**
- When customer calls, retrieve their profile
- Inject context into assistant prompts:
  - "Customer has purchased X, contacted us on [date] about Y"
  - "Customer is VIP (high-value)"
  - "Known issue: complains about Z"
- Assistants reference context naturally in conversations

**FR-9: Conversation Threading**
- Link all calls from same customer into one thread
- Show conversation timeline in CRM
- Allow agents to see full history when escalating

### 3. API & Integration

**FR-10: Call Initiation API**
- Endpoint: `POST /api/calls/initiate`
- Input: customer_phone, optional(assistant_type, crm_data)
- Output: access token, livekit_room_token
- Integration with web/mobile forms

**FR-11: Token Generation**
- Secure, time-limited tokens for frontend
- Tokens scoped to specific customer/call
- Automatic expiry and refresh mechanisms

**FR-12: Webhook Notifications**
- Real-time updates on call events:
  - call_started, sentiment_changed, assistant_switched, call_ended
  - Customer can subscribe to specific events
  - Retry logic for failed webhook deliveries

### 4. Monitoring & Analytics

**FR-13: Call Analytics Dashboard**
- Real-time monitoring:
  - Active calls count
  - Average call duration
  - Routing distribution (% to each assistant)
  - Sentiment distribution (% positive/negative/neutral)
- Historical analytics:
  - Calls per day/week/month
  - Peak hours analysis
  - Customer satisfaction trends
  - Assistant performance comparison

**FR-14: Quality Metrics**
- Track key metrics:
  - Speech recognition accuracy (per call)
  - Sentiment routing correctness
  - Average resolution time per query type
  - Escalation rate (to human agents, if applicable)

**FR-15: Error Handling & Logging**
- Log all errors with full context
- Alert system if:
  - Speech recognition confidence < 70%
  - No response from assistant for > 10 seconds
  - Customer hangs up during call
- Graceful degradation (keep call running, notify support)

---

## Non-Functional Requirements

### Performance

**NFR-1: Response Time**
- Speech recognition latency: < 2 seconds from end of customer sentence
- Assistant response time: < 3 seconds (including STT + LLM + TTS)
- Sentiment analysis: Real-time (parallel with speech recognition)
- API response time: < 200ms for all endpoints (p95)
- Call initiation to first greeting: < 5 seconds

**NFR-2: Concurrent Capacity**
- Minimum: 100 concurrent calls per production instance
- Scalability: Add instances for >100 concurrent calls
- LiveKit backend handles full media stream for all concurrent calls
- Database: Connection pool supports all concurrent connections

**NFR-3: Audio Quality**
- Audio codec: Opus (most efficient for speech)
- Sample rate: 16kHz (sufficient for speech clarity)
- Bitrate: 20-40 kbps (minimal bandwidth without quality loss)
- Latency: < 150ms audio round-trip (network + processing)

### Security

**NFR-4: Authentication & Authorization**
- All API endpoints require authentication (JWT tokens)
- Tokens expire after 1 hour
- Refresh token mechanism for extended sessions
- Role-based access control (RBAC) per customer
- API rate limiting: 10 requests/second per token, 100,000/day

**NFR-5: Data Encryption**
- All data in transit: TLS 1.3 minimum
- Call recordings: AES-256 encryption at rest
- Sensitive data (API keys, customer data): Encrypted in database
- Key rotation every 90 days
- No plaintext passwords stored

**NFR-6: Data Privacy & Compliance**
- GDPR compliant data handling
- Right to be forgotten: Delete all customer data on request
- Call recording consent: Explicit opt-in before recording
- Data residency: Option for EU/MENA data centers
- Audit logging: All access to sensitive data logged
- Regular penetration testing (quarterly)

**NFR-7: PII Protection**
- Phone numbers masked in logs (except for authorized users)
- Call transcripts not logged to plain text
- CRM data field-level encryption
- Automatic PII detection and redaction in transcripts

### Scalability

**NFR-8: Horizontal Scaling**
- FastAPI backend stateless (can scale horizontally)
- Database: Supabase PostgreSQL with read replicas
- LiveKit: Native clustering across multiple servers
- Load balancing: Round-robin across backend instances
- Caching: Redis for frequently accessed data (customer profiles, analytics)

**NFR-9: High Availability**
- 99.5% uptime SLA
- Multi-region deployment ready (same logic works in any region)
- Automatic failover for agent disconnects
- Database replication and backups (daily + transaction logs)
- Health checks on all services (every 10 seconds)

**NFR-10: Data Retention & Archival**
- Active storage: Call recordings + transcripts (30 days hot storage)
- Archive storage: Move to cold storage after 30 days (S3 Glacier)
- Compliance storage: Metadata retained for 7 years (per regulations)
- Automatic cleanup of expired data

### Reliability

**NFR-11: Error Recovery**
- Agent disconnection: Automatic reconnection within 5 seconds
- Partial transcript loss: Keep existing transcript, resume new audio
- LLM/API failures: Graceful fallback to basic assistant
- Network interruptions: Buffer audio, resume when connection restored
- Database unavailability: Maintain in-memory cache for critical operations

**NFR-12: Monitoring & Alerting**
- Real-time dashboards (Grafana/DataDog)
- Alerts for:
  - API error rate > 1%
  - Average response time > 5 seconds
  - Concurrent calls > 90% capacity
  - Database CPU > 80%
  - LiveKit connection failures
- Alert channels: Email, SMS, Slack

**NFR-13: Observability**
- Structured logging (JSON format)
- Distributed tracing across services
- Metrics collection (Prometheus)
- Call quality metrics (jitter, latency, packet loss)
- Performance profiling for slow calls

### Accessibility

**NFR-14: Voice Accessibility**
- Clear, distinct voice output from ElevenLabs
- Adjustable speech speed (customer can request faster/slower)
- Accent support (Syrian, other Arabic dialects)
- Fallback to English if customer requests

**NFR-15: Error Communication**
- Clear error messages in Arabic
- Guidance on how to recover from errors
- Option to repeat request or escalate to human
- No confusing technical jargon in customer-facing messages

### Integration

**NFR-16: Third-Party API Integration**
- OpenAI API: Robust error handling, automatic retries
- ElevenLabs TTS: Voice synthesis with caching
- LiveKit: Reliable media infrastructure
- Supabase: Database operations with connection pooling
- Fallback services: Identify alternatives if primary service fails

**NFR-17: Webhook Reliability**
- Webhook delivery: At-least-once guarantee
- Retry logic: Exponential backoff (1s, 2s, 4s, 8s, 16s, then daily)
- Webhook signature verification: HMAC-SHA256
- Timeout: 30 seconds per webhook call
- Dead-letter queue for failed webhooks

---

## Implementation Planning

### Epic Breakdown Required

Requirements must be decomposed into epics and bite-sized stories (200k context limit).

**Next Step:** Run `/bmad:bmm:workflows:create-epics-and-stories` to create the implementation breakdown.

### Recommended Implementation Sequence

1. **Phase 1 (MVP - Weeks 1-4):** Core call center + sentiment routing
2. **Phase 2 (Week 5-8):** CRM integration + analytics dashboard
3. **Phase 3 (Week 9-12):** Advanced features + multi-dialect support
4. **Phase 4 (Month 4+):** Enterprise features + optimization

---

## References

- **Documentation Index:** [docs/index.md](./index.md)
- **Configuration Analysis:** [CALLCENTER_CONFIGURATION_ANALYSIS.md](./CALLCENTER_CONFIGURATION_ANALYSIS.md)
- **Implementation Guide:** [CALLCENTER_IMPLEMENTATION_GUIDE.md](./CALLCENTER_IMPLEMENTATION_GUIDE.md)
- **Sentiment Routing Guide:** [SENTIMENT_BASED_ROUTING.md](./SENTIMENT_BASED_ROUTING.md)
- **Project Scan Report:** [project-scan-report.json](./project-scan-report.json)

---

## Next Steps

1. **Review & Confirm PRD**
   - Review this document for accuracy and completeness
   - Suggest any modifications needed

2. **Epic & Story Breakdown**
   - Run: `/bmad:bmm:workflows:create-epics-and-stories`
   - This will decompose requirements into implementable stories

3. **Architecture Design**
   - Run: `/bmad:bmm:workflows:architecture`
   - Define technical implementation approach

4. **Sprint Planning**
   - Run: `/bmad:bmm:workflows:sprint-planning`
   - Schedule stories into sprints

---

## Summary

**Ornina AI Call Center** is a sophisticated, 24/7 customer service platform that combines:
- ✨ **Native Arabic Intelligence** with Syrian dialect fluency
- 🔄 **Smart Multi-Assistant Routing** based on real-time sentiment
- ⚡ **Cost-Effective Automation** (70-80% cost reduction vs. human agents)
- 📊 **Enterprise-Grade Reliability** with 99.5% uptime SLA
- 🌍 **Regional Focus** on MENA markets with compliance considerations

The magic is **seamless, culturally-aware AI conversations that customers don't realize are automated**—paired with powerful backend APIs for enterprise integration.

---

**PRD Created:** 2025-11-10
**Author:** mohamed
**Project:** Ornina AI Call Center
**Status:** ✅ Ready for Epic Breakdown
