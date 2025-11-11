# Avatar - Epic Breakdown

**Author:** mohamed
**Date:** 2025-11-10
**Project Level:** Medium-High Complexity
**Target Scale:** 100+ concurrent calls, 10,000+ calls/day

---

## Overview

This document provides the complete epic and story breakdown for **Ornina AI Call Center**, decomposing the requirements from the [PRD](./PRD.md) into implementable stories organized for incremental delivery.

The system is a sophisticated, 24/7 customer service platform combining native Arabic intelligence (Syrian dialect) with smart multi-assistant routing based on real-time sentiment analysis.

**Key Epics (7 major phases):**
1. Foundation & Infrastructure (setup, deployment, environment)
2. Core Audio Call Center (audio handling, multi-persona system)
3. Intelligent Routing & Sentiment (sentiment analysis, dynamic routing)
4. CRM & Customer Context (customer profiles, context injection)
5. API & Backend Integration (REST endpoints, authentication)
6. Analytics & Monitoring (dashboards, metrics, observability)
7. Security, Compliance & Testing (encryption, compliance, validation)

---

## Epic 1: Foundation & Infrastructure

**Goal:** Establish project foundation, deployment pipeline, and core infrastructure enabling all subsequent development.

This is the critical first epic that creates the environment for all other work. It includes repository structure, build systems, Docker containerization, database setup, and CI/CD pipelines.

### Story 1.1: Project Setup & Repository Structure

As a **developer**,
I want to initialize the project structure with proper organization for FastAPI backend, Next.js frontend, and supporting services,
So that the team has a clear, maintainable codebase foundation with proper dependency management.

**Acceptance Criteria:**

**Given** a fresh project initialization
**When** I run the project setup scripts
**Then** the following directory structure exists:
- `callCenter/` - FastAPI backend with modular structure (api, agents, routing, etc.)
- `frontend/` - Next.js dashboard application
- `docs/` - Documentation (PRD, architecture, guides)
- `docker/` - Docker configuration and compose files
- `.env.example` - Environment template with all required variables

**And** the following files are created:
- `requirements.txt` (Python dependencies)
- `package.json` (Node.js dependencies)
- `docker-compose.yml` (multi-service orchestration)
- `.gitignore` (excluding sensitive files)
- `README.md` (project overview)

**And** all dependencies can be installed without errors
**And** the project structure passes lint/format checks

**Prerequisites:** None

**Technical Notes:**
- Use FastAPI for backend (async, modern Python)
- Next.js for frontend (React, SSR)
- Python 3.11+, Node 18+
- Proper virtual environment and node_modules separation
- Environment variables for API keys, database URLs

---

### Story 1.2: Docker Setup & Container Configuration

As a **DevOps engineer**,
I want containerized services for the FastAPI backend, Next.js frontend, and PostgreSQL database,
So that the application can be deployed consistently across development, staging, and production environments.

**Acceptance Criteria:**

**Given** a development machine
**When** I run `docker-compose up`
**Then** the following services start successfully:
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379, optional but recommended)

**And** all services can communicate with each other
**And** database migrations run automatically on startup
**And** volume mounts enable hot-reload for development
**And** environment variables are properly loaded from `.env` files

**Prerequisites:** Story 1.1 (Project Setup)

**Technical Notes:**
- Multi-stage Docker builds for optimized images
- Docker Compose for local development orchestration
- Separate Dockerfiles for backend and frontend
- Health checks for all services
- Proper networking between containers

---

### Story 1.3: Database Schema & Supabase Integration

As a **backend developer**,
I want a PostgreSQL database with properly defined schema for calls, customers, transcripts, and analytics,
So that the application has a reliable data layer with proper relationships and indexing.

**Acceptance Criteria:**

**Given** PostgreSQL database is running
**When** I run migrations
**Then** the following tables exist:
- `users` (customer tenants)
- `customers` (end customers with phone, email, metadata)
- `calls` (call records with metadata, duration, status)
- `transcripts` (call transcripts with sentiment data)
- `sentiments` (sentiment history per call)
- `crm_data` (customer history, preferences, tags)
- `api_tokens` (authentication tokens)
- `webhooks` (webhook configurations and delivery logs)
- `analytics_snapshots` (pre-computed analytics)

**And** proper indexes exist on:
- `calls.customer_id`, `calls.created_at`, `calls.status`
- `customers.phone`, `customers.user_id`
- `transcripts.call_id`
- `api_tokens.token`

**And** foreign key relationships are properly defined
**And** timestamps (created_at, updated_at) exist on all tables
**And** Supabase dashboard shows all tables with proper structure

**Prerequisites:** Story 1.2 (Docker Setup)

**Technical Notes:**
- Use SQLAlchemy for ORM (Python)
- Alembic for migration management
- Indexes on frequently filtered columns (customer_id, created_at)
- Soft deletes for compliance (deleted_at column)
- Row-level security (RLS) for multi-tenancy

---

### Story 1.4: Environment Configuration & Secret Management

As a **DevOps engineer**,
I want a secure system for managing environment variables and secrets across development and production,
So that sensitive information is protected and configuration is environment-specific.

**Acceptance Criteria:**

**Given** the application is deployed
**When** I check the configuration system
**Then** the following environment variables are properly loaded:
- OpenAI API key
- ElevenLabs API key
- LiveKit server URL and API key
- Supabase URL and API key
- Database connection string
- JWT secret key
- Application environment (development/staging/production)

**And** sensitive values are never logged or exposed in error messages
**And** different environments have different configurations
**And** `.env` files are in `.gitignore`
**And** `.env.example` shows all required variables without secrets

**Prerequisites:** Story 1.1 (Project Setup)

**Technical Notes:**
- Use python-dotenv for local development
- Environment variables for all external service credentials
- Separate `.env.development`, `.env.staging`, `.env.production`
- Never commit `.env` files to git
- Document all required variables in `.env.example`

---

### Story 1.5: CI/CD Pipeline & Automated Testing Infrastructure

As a **DevOps engineer**,
I want automated CI/CD pipelines for testing and deployment,
So that code quality is maintained and deployments are reliable and repeatable.

**Acceptance Criteria:**

**Given** code is pushed to the repository
**When** the CI pipeline triggers
**Then** the following checks run automatically:
- Python linting (flake8, black)
- TypeScript/JavaScript linting (ESLint)
- Unit tests (pytest for backend, Jest for frontend)
- Type checking (mypy for Python, tsc for TypeScript)
- Security scanning (bandit for Python, npm audit)

**And** all checks must pass before merging to main
**And** a deployment pipeline exists for production releases
**And** tests report coverage metrics
**And** failed checks block merges

**Prerequisites:** Stories 1.1, 1.2 (Project Setup, Docker)

**Technical Notes:**
- Use GitHub Actions for CI/CD (or similar)
- Automated testing on every PR
- Coverage reports for code quality
- Automated deployment on main branch
- Rollback mechanisms for failed deployments

---

## Epic 2: Core Audio Call Center

**Goal:** Build the foundational audio call center system with multi-persona AI assistants, audio handling, and call management.

This epic delivers the core functionality of handling audio calls, managing multiple AI personas, and recording/transcribing conversations.

### Story 2.1: LiveKit Integration & Audio Infrastructure

As a **backend developer**,
I want to integrate LiveKit for reliable audio communication infrastructure,
So that the system can handle high-quality audio streams for customer calls.

**Acceptance Criteria:**

**Given** a call is initiated
**When** the LiveKit connection is established
**Then** the following occur:
- A new LiveKit room is created with unique room_id
- Customer receives access token to join the room
- Agent/AI receives credentials to join the same room
- Audio stream is established between customer and agent

**And** the connection supports:
- Audio codec: Opus (16kHz, mono)
- Bitrate: 20-40 kbps (bandwidth efficient)
- Latency: <150ms round-trip
- Automatic reconnection on network glitches

**And** room cleanup occurs when call ends
**And** recording hooks are set up for call recordings

**Prerequisites:** Story 1.4 (Environment Configuration)

**Technical Notes:**
- LiveKit Python SDK for backend
- Room naming convention: `call_{call_id}_{timestamp}`
- Access tokens with proper permissions
- Recording to S3 or similar
- Room expiry after call completes

---

### Story 2.2: Multi-Persona Assistant System Setup

As a **backend developer**,
I want to define and configure three AI personas (Reception, Sales, Support) with distinct characteristics,
So that each persona has appropriate tone, knowledge, and response patterns for their role.

**Acceptance Criteria:**

**Given** the system initializes
**When** each assistant is configured
**Then** each persona (Reception, Sales, Support) has:
- Unique system prompt defining behavior and tone
- Voice characteristics (name, tone parameters for ElevenLabs)
- Response style (warm, sales-focused, empathetic)
- Knowledge domain (what each can help with)
- Handoff rules (when to route to another persona)

**And** personas can be updated via configuration
**And** each persona has consistent behavior within their domain
**And** personas respect tone parameters (friendly vs. professional)

**Persona Details:**
1. **Ahmed (Reception)** - Warm, welcoming, gathers initial information
2. **Sarah (Sales)** - Enthusiastic, product-focused, drives conversions
3. **Mohammed (Support)** - Empathetic, solution-focused, problem solver

**Prerequisites:** Story 1.3 (Database Schema)

**Technical Notes:**
- Store persona configs in database
- System prompts should be detailed but concise
- ElevenLabs voice IDs per persona
- Tone parameters (speed, pitch, warmth)
- Easy update mechanism for customization

---

### Story 2.3: Speech-to-Text (STT) Integration

As a **backend developer**,
I want to convert customer audio to Arabic text with high accuracy,
So that the AI assistant can understand and respond to customer queries.

**Acceptance Criteria:**

**Given** a customer speaks in Arabic (Syrian dialect)
**When** their audio is processed
**Then** speech-to-text produces:
- Accurate transcription (>90% accuracy for Syrian dialect)
- Timing information (when each phrase was spoken)
- Confidence scores for each phrase
- Fallback to Modern Standard Arabic if needed

**And** the following are handled:
- Background noise tolerance
- Multiple speakers (distinguishing customer from ambient)
- Unclear speech (confidence scores indicate reliability)
- Accents and dialect variations

**Prerequisites:** Story 2.1 (LiveKit Integration)

**Technical Notes:**
- Use OpenAI Whisper API for robust Arabic support
- Stream audio as it arrives (no need to wait for silence)
- Confidence scores for quality assessment
- Cache frequently recognized phrases
- Handle long silence (pause detection)

---

### Story 2.4: Text-to-Speech (TTS) & Voice Synthesis

As a **backend developer**,
I want to convert assistant responses to natural-sounding Arabic audio,
So that customers have natural conversations with the AI.

**Acceptance Criteria:**

**Given** an AI assistant generates a text response
**When** the text is converted to speech
**Then** audio output has:
- Natural pronunciation of Arabic/Syrian dialect
- Appropriate speed (adjustable, default 1.0x)
- Proper intonation and emphasis
- Consistent voice matching the persona

**And** the following features work:
- Voice characteristics match persona (warm, professional, etc.)
- Numbers and abbreviations are pronounced correctly
- Punctuation influences tone (questions, statements, excitement)
- Streaming output (audio starts playing quickly)

**Prerequisites:** Story 2.2 (Multi-Persona Assistant System)

**Technical Notes:**
- ElevenLabs API for high-quality Arabic voices
- Persona-specific voice IDs
- Pre-generate common responses for faster delivery
- Cache synthesized audio (same response = same audio)
- Streaming TTS for low latency

---

### Story 2.5: AI Assistant Response Engine

As a **backend developer**,
I want the AI assistant to generate contextual responses using OpenAI GPT-4,
So that conversations feel natural and helpful.

**Acceptance Criteria:**

**Given** a customer message is transcribed
**When** the assistant processes the message
**Then** the response:
- Is generated using GPT-4 Turbo (or latest available)
- Respects the persona's system prompt
- Maintains conversation context (previous messages)
- Includes relevant customer information if available
- Responds within <3 seconds

**And** the following are handled:
- Long conversations (token counting, context window management)
- Instruction injection (users can't override system prompt)
- Hallucination prevention (staying within knowledge domain)
- Graceful failures (fallback response if API fails)

**Prerequisites:** Stories 2.2, 2.3 (Persona System, STT)

**Technical Notes:**
- OpenAI API with GPT-4 Turbo
- Token counting to manage context window
- System prompt injection protection
- Conversation history stored in database
- Timeout handling for slow API responses

---

### Story 2.6: Call Recording & Storage

As a **backend developer**,
I want to record all calls automatically and store them securely,
So that calls can be reviewed, analyzed, and maintained for compliance.

**Acceptance Criteria:**

**Given** a call is in progress
**When** LiveKit records the audio
**Then** the recording:
- Is captured in high quality (16kHz, mono)
- Is stored securely (AES-256 encryption)
- Includes metadata (call_id, start_time, end_time, participants)
- Can be downloaded by authorized users
- Is archived to cold storage after 30 days

**And** the following are supported:
- Recording consent verification
- Per-call recording preferences
- Automatic cleanup of old recordings
- Integrity verification (checksums)
- Access audit trail

**Prerequisites:** Story 2.1 (LiveKit Integration)

**Technical Notes:**
- LiveKit recording to S3 bucket
- AES-256 encryption for stored files
- Metadata stored in database
- S3 lifecycle policies for archival
- Signed URLs for secure downloads

---

### Story 2.7: Call Transcript Generation & Storage

As a **backend developer**,
I want to generate transcripts from call recordings with timestamps,
So that customers and agents can review what was said.

**Acceptance Criteria:**

**Given** a call has completed
**When** the transcript is generated
**Then** the transcript includes:
- Speaker identification (customer vs. assistant)
- Timestamps for each exchange
- Full conversation text
- Sentiment annotations (per message)
- Confidence scores where applicable

**And** the transcript is:
- Stored securely in database
- Searchable for keywords
- Downloadable in multiple formats (TXT, JSON, PDF)
- Redactable (PII can be masked)

**Prerequisites:** Stories 2.3, 2.6 (STT, Call Recording)

**Technical Notes:**
- Use Whisper for transcript generation from recordings
- Store transcripts in database with full-text search index
- Timestamp precision: 1 second granularity
- Sentiment scores from separate sentiment engine
- PDF generation for export

---

## Epic 3: Intelligent Routing & Sentiment Analysis

**Goal:** Implement real-time sentiment analysis and intelligent routing to ensure customers reach the right assistant for their needs.

This epic delivers the innovation of the system - seamless, sentiment-driven assistant transitions that feel natural to the customer.

### Story 3.1: Sentiment Analysis Engine

As a **backend developer**,
I want to analyze customer sentiment in real-time as they speak,
So that the system can determine which assistant is best suited to help.

**Acceptance Criteria:**

**Given** a customer is speaking
**When** their speech is transcribed
**Then** sentiment analysis produces:
- Sentiment classification: Positive, Negative, Neutral, Interested, Complaining
- Confidence score (0-100) for classification
- Emotional tone indicators (frustration, happiness, urgency)
- Trend over time (sentiment improving or degrading)

**And** sentiment is:
- Calculated in real-time (parallel with STT)
- Continuously updated as conversation progresses
- Stored with transcript for analysis
- Accurate (>85% confidence for routing decisions)

**Prerequisites:** Story 2.3 (Speech-to-Text)

**Technical Notes:**
- Use OpenAI API or dedicated sentiment analysis service
- Real-time analysis of transcribed text
- Confidence thresholds for different sentiment categories
- Emotion detection (anger, frustration, happiness)
- Context-aware analysis (sarcasm handling)

---

### Story 3.2: Sentiment-Based Routing Logic

As a **backend developer**,
I want to implement routing rules that automatically direct customers to the best assistant based on sentiment,
So that customers get appropriate help without explicit menu navigation.

**Acceptance Criteria:**

**Given** sentiment analysis produces a classification
**When** routing logic is applied
**Then** the following rules execute:
- Positive/Interested sentiment → Route to Sarah (Sales)
- Negative/Complaining sentiment → Route to Mohammed (Support)
- Neutral/Information sentiment → Keep with Ahmed (Reception) or route based on query
- Confidence score threshold (>85%) triggers routing

**And** the following edge cases are handled:
- Mixed sentiment (some positive, some negative) → Route to Support
- Very low confidence → Keep current assistant, request clarification
- Repeated routing to same assistant → Stop re-routing
- Customer explicitly asks for different assistant → Honor request

**Prerequisites:** Story 3.1 (Sentiment Analysis)

**Technical Notes:**
- Database table for routing rules (can be updated)
- Avoid re-routing more than once per conversation
- Track routing decisions for quality analysis
- A/B testing framework for rule optimization
- Gradual rollout (test with subset of calls first)

---

### Story 3.3: Seamless Assistant Transitions with Context

As a **backend developer**,
I want to transition customers between assistants smoothly while preserving conversation context,
So that handoffs feel natural and customers don't need to repeat themselves.

**Acceptance Criteria:**

**Given** routing decision is made to switch assistants
**When** the transition occurs
**Then** the following happen in order:
1. Current assistant finishes current thought (completes sentence)
2. New assistant is loaded with full conversation history
3. New assistant acknowledges context naturally: "I see you were interested in..."
4. Customer is unaware they're talking to a different assistant
5. Transition completes in <2 seconds

**And** the transition includes:
- Full conversation history (all previous messages)
- Customer profile and CRM context
- Previous assistant's assessment of customer needs
- Call metadata (duration so far, sentiment history)

**Prerequisites:** Stories 3.2 (Routing Logic), 2.2 (Persona System)

**Technical Notes:**
- Manage conversation state in database/memory
- LLM context injection for new assistant
- Timing orchestration (finish current response before switching)
- Error handling if new assistant fails to load
- Track transition quality for optimization

---

### Story 3.4: Sentiment Routing Quality Validation

As a **QA engineer**,
I want to validate that sentiment-based routing is working correctly and improving customer satisfaction,
So that we can measure routing accuracy and optimize the system.

**Acceptance Criteria:**

**Given** a sample of completed calls
**When** routing validation is performed
**Then** the following metrics are calculated:
- Routing accuracy: % of cases where customer was satisfied with routing
- False positives: % of misrouted customers
- False negatives: % of customers who should have been routed differently
- Sentiment prediction accuracy vs. customer satisfaction survey

**And** data is collected through:
- Post-call NPS survey (1-10 scale)
- Customer feedback: "Were you helped by the right assistant?"
- Conversation quality review (human assessment)
- Time to resolution by routing path

**Prerequisites:** Stories 3.1, 3.2 (Sentiment Analysis, Routing)

**Technical Notes:**
- Collect A/B testing data
- NPS surveys after calls (via SMS or email)
- Sample human review of conversations
- Statistical significance testing
- Feedback loop to improve routing rules

---

## Epic 4: CRM & Customer Context

**Goal:** Build customer relationship management capabilities with context injection so assistants have relevant customer history.

This epic makes conversations more personalized by providing assistants with customer background and history.

### Story 4.1: Customer Profile Management

As a **backend developer**,
I want to store and manage customer profiles with contact info and history,
So that customer information is centralized and accessible.

**Acceptance Criteria:**

**Given** a new customer calls
**When** their phone number is looked up
**Then** a customer profile is created/retrieved with:
- Phone number (primary identifier)
- Name
- Email address
- Physical address
- Customer tier (Starter, Professional, Enterprise)
- VIP status (if applicable)
- Preferred language

**And** the profile includes historical data:
- First contact date
- Total calls to date
- Customer lifetime value
- Common issues/topics
- Preferences (callback time, language, etc.)

**And** profiles can be:
- Created manually via API
- Updated via API or dashboard
- Linked to multiple phone numbers (same customer)
- Deleted with proper data handling (GDPR compliance)

**Prerequisites:** Story 1.3 (Database Schema)

**Technical Notes:**
- Customer table in database
- Phone number as primary lookup key
- Support for multiple phone numbers per customer
- Soft deletes for compliance
- Audit trail of profile changes

---

### Story 4.2: Conversation History Threading

As a **backend developer**,
I want to link all calls from the same customer into a conversation thread,
So that agents and customers can see the full history of their interactions.

**Acceptance Criteria:**

**Given** a customer has made multiple calls
**When** their profile is viewed
**Then** all calls are displayed in chronological order:
- Call date/time
- Duration
- Initial sentiment
- Assistant(s) involved
- Brief summary of topic
- Resolution status

**And** conversation threading includes:
- Linkage of related issues
- Cross-call context (issue from call 1, follow-up in call 3)
- Tags/categories per call
- Open issues vs. resolved
- Customer journey visualization

**Prerequisites:** Story 4.1 (Customer Profiles)

**Technical Notes:**
- calls table with customer_id foreign key
- Timeline view in dashboard
- Search/filter by topic or date
- Thread summarization
- Integration with CRM features

---

### Story 4.3: Context Injection into Assistant Prompts

As a **backend developer**,
I want to automatically include relevant customer context in assistant prompts,
So that assistants can reference customer history and provide personalized responses.

**Acceptance Criteria:**

**Given** a call starts with a returning customer
**When** the first assistant prompt is generated
**Then** the system prompt includes:
- Customer name and history
- Previous issues and resolutions
- Known preferences
- VIP status
- Relevant context: "Customer purchased X, contacted about Y on [date]"

**And** the context is formatted to:
- Fit within token limits
- Highlight recent interactions
- Provide actionable information
- Not overwhelm with irrelevant details

**And** the assistant naturally references context:
- "I see you called about our product X last week..."
- "Based on your account, you're a Professional customer..."
- "Following up on your support ticket from Tuesday..."

**Prerequisites:** Stories 4.1, 2.5 (Customer Profiles, Response Engine)

**Technical Notes:**
- Dynamic prompt construction based on customer data
- Token budgeting for context inclusion
- Prioritization of recent/relevant info
- Caching for performance
- Testing with realistic customer data

---

### Story 4.4: CRM Data Import & Synchronization

As a **product manager**,
I want to import customer data from external CRM systems or spreadsheets,
So that existing customer relationships are available to assistants.

**Acceptance Criteria:**

**Given** customer data exists in external systems
**When** import is performed
**Then** the following data is synchronized:
- Customer contact information (name, phone, email)
- Purchase history (what they've bought)
- Support history (issues they've had)
- Customer preferences
- Account metadata

**And** import handles:
- CSV/Excel file uploads
- API integration with Salesforce/HubSpot (if needed)
- Duplicate detection (same customer, multiple entries)
- Data validation and error reporting
- Scheduled sync for ongoing updates

**Prerequisites:** Story 4.1 (Customer Profiles)

**Technical Notes:**
- CSV parser for data import
- Duplicate detection algorithm (phone match, name similarity)
- Data validation and mapping
- Error logging and reporting
- Audit trail of imports

---

## Epic 5: API & Backend Integration

**Goal:** Build RESTful APIs for external integrations and token management.

This epic provides the interfaces that customers' systems use to interact with the call center.

### Story 5.1: Authentication & JWT Token System

As a **backend developer**,
I want to implement JWT-based authentication with API keys and token generation,
So that API access is secure and properly scoped.

**Acceptance Criteria:**

**Given** a customer (tenant) wants to make API calls
**When** they authenticate
**Then** the following flow occurs:
1. Customer provides API key + secret
2. System validates credentials
3. JWT token is generated (1-hour expiry)
4. Token includes customer_id and scoped permissions

**And** tokens are:
- Validated on every API request
- Automatically expired after 1 hour
- Refreshable via refresh token mechanism
- Revocable (invalidated immediately)
- Rate-limited (10 req/sec per token)

**And** the system supports:
- Multiple API keys per customer
- Granular permissions (customer_read, customer_write, admin_write, etc.)
- Token revocation via dashboard
- Audit log of token generation/usage

**Prerequisites:** Story 1.3 (Database Schema)

**Technical Notes:**
- PyJWT for token generation
- Secret key stored securely
- Token payload includes customer_id, permissions, expiry
- Refresh token rotation on use
- Comprehensive audit logging

---

### Story 5.2: Call Initiation API Endpoint

As a **frontend developer**,
I want to call an API to initiate a new call,
So that the dashboard can start calls programmatically.

**Acceptance Criteria:**

**Given** a frontend application wants to start a call
**When** POST /api/calls/initiate is called with:
```
{
  "customer_phone": "+963-XXX-XXXXX",
  "assistant_type": "reception" (optional),
  "crm_context": {} (optional)
}
```

**Then** the response includes:
```
{
  "call_id": "call_123456",
  "livekit_room": "call_123456_1234567890",
  "livekit_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "status": "initiated",
  "expires_in": 3600
}
```

**And** the API:
- Validates customer phone format
- Creates call record in database
- Generates LiveKit room token
- Sets call expiry (1 hour)
- Triggers assistant to join room

**Prerequisites:** Stories 5.1, 2.1 (JWT Auth, LiveKit)

**Technical Notes:**
- FastAPI endpoint design
- Input validation
- Error handling (invalid phone, rate limits)
- Logging for debugging
- Integration with call initiation flow

---

### Story 5.3: Call Metadata & History Retrieval

As a **frontend developer**,
I want to retrieve call details and history via API,
So that I can display call information in the dashboard.

**Acceptance Criteria:**

**Given** a user wants call information
**When** GET /api/calls/{call_id} is called
**Then** response includes:
```
{
  "call_id": "call_123456",
  "customer_phone": "+963-123-4567",
  "duration": 450,
  "start_time": "2025-11-10T10:30:00Z",
  "end_time": "2025-11-10T10:38:00Z",
  "status": "completed",
  "assistants": ["reception", "sales"],
  "sentiment_history": [...],
  "transcript_url": "/api/transcripts/call_123456",
  "recording_url": "/api/recordings/call_123456"
}
```

**And** GET /api/calls (list endpoint) supports:
- Filtering by date range
- Filtering by customer
- Filtering by sentiment
- Pagination (limit, offset)
- Sorting options

**Prerequisites:** Story 5.2 (Call Initiation API)

**Technical Notes:**
- Proper pagination for large result sets
- Authorization checks (user can only see own tenant's calls)
- Caching for performance
- Indexed queries for fast retrieval

---

### Story 5.4: Webhook Notifications System

As a **backend developer**,
I want to send webhooks to customers when important events occur,
So that customer systems can react to call events in real-time.

**Acceptance Criteria:**

**Given** a call event occurs (started, ended, routed, etc.)
**When** event is generated
**Then** webhooks are sent to customer-registered endpoints with:
```
{
  "event_type": "call_started",
  "call_id": "call_123456",
  "timestamp": "2025-11-10T10:30:00Z",
  "data": { ... }
}
```

**And** webhooks include:
- HMAC-SHA256 signature for verification
- Retry logic (exponential backoff: 1s, 2s, 4s, 8s, 16s, then daily)
- At-least-once delivery guarantee
- Dead-letter queue for failed deliveries
- Customer can configure which events to receive

**And** events supported:**
- call_started
- call_ended
- sentiment_changed
- assistant_switched
- call_recording_ready
- call_transcript_ready

**Prerequisites:** Story 1.3 (Database Schema)

**Technical Notes:**
- Webhook storage in database
- Event queue/queue service for reliable delivery
- HMAC signature generation and verification
- Retry mechanism with exponential backoff
- Dead-letter handling for permanently failed webhooks

---

## Epic 6: Analytics & Monitoring

**Goal:** Provide dashboards and metrics for monitoring system health and call analytics.

This epic enables visibility into system performance and customer behavior.

### Story 6.1: Real-Time Call Analytics Dashboard

As a **customer**,
I want to see real-time analytics about my calls on a dashboard,
So that I understand call volume, routing, and sentiment trends.

**Acceptance Criteria:**

**Given** I log into the dashboard
**When** I view the analytics page
**Then** I see real-time metrics:
- **Active calls:** Current number of ongoing calls
- **Average duration:** Mean call length
- **Sentiment distribution:** Pie chart of positive/negative/neutral
- **Routing distribution:** % of calls to each assistant
- **Calls per hour:** Trend graph
- **Peak times:** When most calls occur

**And** the dashboard includes:
- Date range selector (last 24h, 7d, 30d, custom)
- Filters by assistant or sentiment
- Export to CSV/PDF
- Real-time updates (refresh every 10 seconds)

**Prerequisites:** Story 6.2 (Analytics Data Collection)

**Technical Notes:**
- Real-time data from Redis or in-memory cache
- WebSocket for live updates
- Charting library (Chart.js, Recharts)
- Performance optimization for large datasets
- Mobile-responsive design

---

### Story 6.2: Analytics Data Collection & Aggregation

As a **backend developer**,
I want to collect and aggregate analytics metrics from calls,
So that dashboards can display accurate, up-to-date statistics.

**Acceptance Criteria:**

**Given** calls are occurring
**When** they complete
**Then** the following metrics are computed and stored:
- Call duration, start time, end time
- Assistant(s) involved
- Sentiment progression (initial vs. final)
- Routing decisions (why assistant was chosen)
- Call outcome (resolved, escalated, etc.)

**And** aggregate metrics are computed:
- Hourly call counts
- Average sentiment by hour/day
- Routing accuracy metrics
- Assistant performance comparison
- Customer satisfaction trends

**And** data is stored for:
- Real-time dashboards (Redis, last 24 hours)
- Historical analysis (database, all data)
- Archival (cold storage after 90 days)

**Prerequisites:** Stories 2.6, 2.7 (Call Recording, Transcripts)

**Technical Notes:**
- Real-time metrics in Redis
- Batch aggregation jobs for historical data
- Separate analytics table for pre-computed metrics
- Retention policies (24h hot, 90d warm, 7yr archive)
- Efficient query design for dashboard

---

### Story 6.3: Error & Performance Monitoring

As a **DevOps engineer**,
I want real-time monitoring of system health, errors, and performance,
So that I can detect and respond to issues quickly.

**Acceptance Criteria:**

**Given** the system is running
**When** I view the monitoring dashboard
**Then** I see:
- **API error rate:** % of requests resulting in errors
- **Response time:** p50, p95, p99 latency
- **Concurrent calls:** Current and capacity usage
- **Database performance:** Query latency, connection pool
- **Service health:** Status of FastAPI, PostgreSQL, LiveKit, OpenAI API

**And** alerts are triggered when:
- Error rate > 1%
- Response time p95 > 5 seconds
- Concurrent calls > 90% capacity
- Database CPU > 80%
- Any service is down

**And** alerts are sent via:
- Email notifications
- Slack integration
- SMS for critical issues
- PagerDuty for on-call escalation

**Prerequisites:** Stories 1.5, 2.1 (CI/CD, LiveKit)

**Technical Notes:**
- Prometheus for metrics collection
- Structured logging (JSON format)
- OpenTelemetry for distributed tracing
- Grafana for dashboards
- Alert manager for notification routing

---

### Story 6.4: Call Quality Metrics & Reporting

As a **operations manager**,
I want detailed metrics on call quality and outcomes,
So that I can identify issues and optimize the system.

**Acceptance Criteria:**

**Given** calls are completed
**When** quality metrics are generated
**Then** reports include:
- **Speech recognition accuracy:** % of correct transcription
- **Assistant response quality:** Manual review scoring
- **Customer satisfaction:** NPS scores from post-call survey
- **Resolution rate:** % of calls that resolved customer issue
- **Escalation rate:** % escalated to human agents
- **Sentiment routing accuracy:** % correctly routed vs. optimal

**And** metrics are available:
- Per call
- Per assistant
- Per time period
- Aggregated across all calls

**And** reports include:
- Trend analysis (improving or degrading)
- Comparison to benchmarks
- Recommendations for improvement

**Prerequisites:** Stories 6.2, 3.4 (Analytics, Routing Validation)

**Technical Notes:**
- Quality scoring framework
- NPS survey integration
- Manual review queue for sample calls
- Statistical analysis of trends
- Executive summary generation

---

## Epic 7: Security, Compliance & Testing

**Goal:** Implement security measures, compliance requirements, and comprehensive testing.

This epic ensures the system is secure, reliable, and ready for production.

### Story 7.1: Data Encryption & Secure Storage

As a **security engineer**,
I want all sensitive data encrypted both in transit and at rest,
So that customer data is protected from unauthorized access.

**Acceptance Criteria:**

**Given** sensitive data is stored or transmitted
**When** encryption is applied
**Then** the following protections exist:
- **In transit:** TLS 1.3 for all API endpoints
- **At rest:** AES-256 encryption for:
  - Call recordings
  - Transcripts containing PII
  - Customer CRM data
  - API keys and secrets
- **Key management:** Keys rotated every 90 days
- **No plaintext:** No passwords, API keys, or PII in plaintext

**And** encryption is:
- Applied transparently (application doesn't see plaintext)
- Verified (checksums ensure integrity)
- Auditable (track all encryption operations)

**Prerequisites:** Story 1.3 (Database Schema)

**Technical Notes:**
- TLS certificates from trusted CA
- Database-level encryption (Supabase has built-in support)
- Field-level encryption for specific sensitive data
- Key vault for managing encryption keys
- Encryption key rotation policies

---

### Story 7.2: GDPR & Data Privacy Compliance

As a **compliance officer**,
I want the system to comply with GDPR and regional data protection laws,
So that the company avoids legal liability and customer data is protected.

**Acceptance Criteria:**

**Given** GDPR requirements apply to the system
**When** data handling occurs
**Then** the following are implemented:
- **Right to access:** Customers can download their data
- **Right to deletion:** Customers can request all data deletion (right to be forgotten)
- **Data portability:** Customers can export data in standard formats
- **Consent management:** Recording/processing consent is required
- **Data processing agreements:** DPAs in place with subprocessors
- **Privacy by design:** Minimal data collection, pseudonymization

**And** compliance is:
- Documented (privacy policy reflects implementation)
- Auditable (logs show who accessed what, when)
- Tested (regular compliance audits)

**Prerequisites:** Story 7.1 (Encryption)

**Technical Notes:**
- Privacy policy documentation
- Consent management system
- Data deletion/redaction procedures
- Data subject request handling (API or manual)
- Regular compliance audits
- Data Processing Agreements with OpenAI, ElevenLabs, etc.

---

### Story 7.3: Authentication & Authorization Testing

As a **QA engineer**,
I want to test that only authorized users can access specific resources,
So that the system properly enforces security boundaries.

**Acceptance Criteria:**

**Given** the authentication system is implemented
**When** tests are run
**Then** the following are verified:
- Invalid tokens are rejected
- Expired tokens are rejected
- Tokens with insufficient permissions are rejected
- Users can only access their own tenant's data
- Cross-tenant access is impossible
- Rate limiting prevents token abuse

**And** test cases cover:
- Valid token scenarios
- Expired token scenarios
- Tampered token scenarios
- Missing token scenarios
- Rate limit bypass attempts

**Prerequisites:** Story 5.1 (JWT Auth)

**Technical Notes:**
- Unit tests for token validation
- Integration tests for endpoint authorization
- Security testing tools (OWASP ZAP, Burp)
- Penetration testing for auth bypass
- Token revocation testing

---

### Story 7.4: Integration Testing & End-to-End Validation

As a **QA engineer**,
I want comprehensive integration tests that validate the entire call flow,
So that all components work together correctly before production.

**Acceptance Criteria:**

**Given** the full system is deployed
**When** integration tests are run
**Then** complete call flows are tested:
1. **Call initiation:**
   - API call creates call record
   - LiveKit room is created
   - Customer receives token

2. **Call execution:**
   - Customer audio flows through LiveKit
   - STT produces correct transcription
   - Sentiment analysis works
   - Assistant generates appropriate response
   - TTS synthesizes audio
   - Audio is sent back to customer

3. **Call completion:**
   - Call is marked complete
   - Recording is stored securely
   - Transcript is generated
   - Analytics metrics are computed
   - Webhook is sent to customer (if configured)

**And** tests validate:
- End-to-end latency (<5 seconds for full round-trip)
- Data integrity (no lost messages)
- Error recovery (graceful handling of failures)
- Concurrent call handling (multiple simultaneous calls)

**Prerequisites:** All stories from Epics 2-6

**Technical Notes:**
- Test call scenarios (happy path, error cases)
- Load testing (100+ concurrent calls)
- Latency testing (measure round-trip times)
- Data consistency checks
- Failure injection testing

---

### Story 7.5: Load Testing & Performance Validation

As a **DevOps engineer**,
I want to validate that the system can handle production-level load,
So that performance meets SLA requirements.

**Acceptance Criteria:**

**Given** the system is deployed
**When** load testing is performed
**Then** the following are validated:
- **Concurrent capacity:** 100+ simultaneous calls
- **Response latency:** API calls <200ms (p95)
- **Assistant latency:** Full response cycle <3 seconds
- **Database performance:** Query times remain <100ms under load
- **Error rate:** <1% under sustained load
- **Graceful degradation:** Proper behavior when capacity exceeded

**And** tests simulate:
- Realistic call distribution (peak hours, off-peak)
- Various call scenarios (long calls, rapid calls, silent calls)
- Network conditions (latency, packet loss)
- Service failures (one service failing, system recovers)

**Prerequisites:** All stories from Epics 1-6

**Technical Notes:**
- Load testing tools (k6, JMeter)
- Production-like test environment
- Baseline metrics for comparison
- Bottleneck identification
- Optimization recommendations

---

### Story 7.6: Security Penetration Testing

As a **security engineer**,
I want to conduct penetration testing to identify vulnerabilities,
So that security risks are mitigated before production.

**Acceptance Criteria:**

**Given** the system is ready for security audit
**When** penetration testing is performed
**Then** tests cover:
- **API security:** SQL injection, command injection, XSS
- **Authentication:** Token bypass, privilege escalation
- **Data protection:** Encryption verification, PII exposure
- **Access control:** Cross-tenant access, privilege abuse
- **Business logic:** Routing abuse, quota bypass
- **Infrastructure:** Default credentials, exposed endpoints

**And** findings are:
- Documented with severity levels
- Remediated before production
- Re-tested to confirm fixes

**Prerequisites:** Stories 7.1, 7.3 (Encryption, Auth Testing)

**Technical Notes:**
- Security assessment tools (OWASP ZAP, Burp Suite)
- Manual security code review
- Threat modeling exercise
- Vulnerability management process
- Security incident response plan

---

### Story 7.7: Production Readiness Validation & Launch

As a **product manager**,
I want a comprehensive checklist to ensure the system is production-ready,
So that we can launch with confidence.

**Acceptance Criteria:**

**Given** all stories are completed
**When** production readiness is evaluated
**Then** the following are confirmed:

**Functionality:**
- ✅ All FRs from PRD are implemented
- ✅ All acceptance criteria are met
- ✅ E2E tests pass
- ✅ Load tests validate performance

**Security:**
- ✅ Encryption at rest and in transit
- ✅ Authentication & authorization working
- ✅ Penetration testing complete
- ✅ No OWASP top 10 vulnerabilities

**Compliance:**
- ✅ GDPR compliance verified
- ✅ Data privacy policies documented
- ✅ Audit logging enabled
- ✅ Data deletion processes tested

**Operations:**
- ✅ Monitoring dashboards deployed
- ✅ Alert system configured
- ✅ Backup/recovery procedures tested
- ✅ Incident response plan ready
- ✅ Documentation complete
- ✅ Support playbooks ready

**Infrastructure:**
- ✅ Database backups working
- ✅ Multi-region deployment possible
- ✅ Auto-scaling configured
- ✅ Health checks on all services

**And** a launch plan exists with:
- Gradual rollout schedule
- Rollback procedures
- Customer onboarding plan
- Support escalation paths

**Prerequisites:** All stories from Epics 1-6

**Technical Notes:**
- Production readiness checklist
- Sign-off process
- Customer communication plan
- Monitoring setup
- Post-launch support plan

---

## Implementation Sequence & Dependencies

### Phase 1: Foundation (Week 1)
- Stories: 1.1 - 1.5
- Output: Project setup, Docker, database, CI/CD ready

### Phase 2: Core Audio (Week 2-3)
- Stories: 2.1 - 2.7
- Dependencies: Complete Phase 1
- Output: Audio calling, personas, recording working

### Phase 3: Intelligence (Week 3-4)
- Stories: 3.1 - 3.4
- Dependencies: Complete Phase 2
- Output: Sentiment analysis, routing, transitions

### Phase 4: Customer Context (Week 4)
- Stories: 4.1 - 4.4
- Dependencies: Complete Phase 3
- Output: CRM, customer profiles, context injection

### Phase 5: APIs (Week 4-5)
- Stories: 5.1 - 5.4
- Dependencies: Complete Phase 1, 2
- Output: REST APIs, webhooks, token system

### Phase 6: Analytics (Week 5)
- Stories: 6.1 - 6.4
- Dependencies: Complete Phase 2, 5
- Output: Dashboards, metrics, monitoring

### Phase 7: Security & Launch (Week 5-6)
- Stories: 7.1 - 7.7
- Dependencies: Complete all previous phases
- Output: Production-ready system

---

## Story Sizing & Effort Estimates

| Epic | Stories | Effort | Complexity |
|------|---------|--------|-----------|
| **Foundation** | 1.1-1.5 | 15-20 hours | Low |
| **Core Audio** | 2.1-2.7 | 40-50 hours | Medium |
| **Intelligent Routing** | 3.1-3.4 | 20-25 hours | Medium |
| **CRM & Context** | 4.1-4.4 | 20-25 hours | Low-Medium |
| **APIs** | 5.1-5.4 | 25-30 hours | Low-Medium |
| **Analytics** | 6.1-6.4 | 25-30 hours | Low-Medium |
| **Security & Testing** | 7.1-7.7 | 35-40 hours | Medium-High |
| **Total** | 27 stories | 180-220 hours | Medium-High |

**Estimated Timeline:** 4-6 weeks with 1 developer, 2-3 weeks with 2+ developers

---

## Story Implementation Notes

Each story should be implemented as a vertically-sliced feature:
- **Not**: Database schema → Backend API → Frontend UI
- **Yes**: Complete feature end-to-end (schema + API + UI + tests)

Each story should have:
- ✅ Acceptance criteria that are testable
- ✅ Clear prerequisites (dependencies)
- ✅ Technical implementation guidance
- ✅ Passing unit & integration tests
- ✅ Documentation updates

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._
