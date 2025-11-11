# Ornina AI Call Center - Documentation Index

**Project:** Ornina AI Call Center Platform
**Status:** 70% Complete - MVP Completion Sprint Ready
**Target Launch:** End of November 2025 (3 weeks)
**Last Updated:** 2025-11-10

---

## 🚀 Quick Start by Role

### Product Managers & Stakeholders
**Want to understand the project, timeline, and status?**

1. **[PRD.md](./PRD.md)** (20 min) - Complete product vision, requirements, and success criteria
2. **[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)** (15 min) - 3-phase timeline, resources, metrics
3. **[EPIC_COMPLETION_STATUS.md](./EPIC_COMPLETION_STATUS.md)** (10 min) - What's done, what's missing, critical issues

**Key Insight:** 70% complete. MVP ready in 1 week with sentiment routing integration.

---

### Backend Engineers (Implementation)
**Want to start building?**

1. **[MVP_COMPLETION_PLAN.md](./MVP_COMPLETION_PLAN.md)** (20 min) - This week's sprint tasks and timeline
2. **[epics.md](./epics.md)** (30 min) - Find your assigned story and acceptance criteria
3. **[CALLCENTER_IMPLEMENTATION_GUIDE.md](./CALLCENTER_IMPLEMENTATION_GUIDE.md)** (20 min) - Technical how-to and code examples
4. **[SENTIMENT_BASED_ROUTING.md](./SENTIMENT_BASED_ROUTING.md)** (15 min) - Core routing logic

**Key Insight:** Start with sentiment routing integration (6-8 hours to fix core feature).

---

### DevOps / Infrastructure
**Want to deploy and maintain?**

1. **[SYSTEM_STATUS.md](./SYSTEM_STATUS.md)** (10 min) - Current infrastructure state
2. **[DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)** (15 min) - How to deploy
3. **[CALLCENTER_CONFIGURATION_ANALYSIS.md](./CALLCENTER_CONFIGURATION_ANALYSIS.md)** (15 min) - Config details

**Key Insight:** Infrastructure 95% ready. All services Docker-based and deployed.

---

### Architecture / Tech Leads
**Want to understand technical decisions?**

1. **[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)** (20 min) - 3-phase plan and decisions
2. **[epics.md](./epics.md)** - Epic overview and technical approach (30 min)
3. **[PRD.md](./PRD.md#api-backend--saas-specific-requirements)** - Technical requirements (10 min)
4. **[EPIC_COMPLETION_STATUS.md](./EPIC_COMPLETION_STATUS.md)** - Gap analysis and tech debt (20 min)

**Key Insight:** 7 epics, sentiment routing is critical gap, Phase 2 needs production hardening.

---

## 📚 Core Documentation

### Strategic Documents
**For understanding vision, requirements, and timeline**

---

## 🏗️ System Architecture

### Project Structure

This is a **multi-part project** with 3 distinct components:

```
/var/www/avatar/
├── avatary/              ← Video Avatar Backend (Python + LiveKit + Tavus)
│   └── Status: ✅ WORKING
│
├── callCenter/           ← Audio Call Center Backend (Python + FastAPI + OpenAI)
│   └── Status: ⚠️ API working, Agent worker needs to be started
│
└── frontend/             ← Shared Next.js Frontend
    ├── /avatar/*         → Avatar video call routes
    └── /callcenter/*     → Call center audio routes
```

### Technology Stack

#### Part 1: Avatary (Video Avatar Backend)

- **Language:** Python 3.11
- **Framework:** LiveKit Agents SDK
- **Video:** Tavus API (video avatars)
- **Audio:** ElevenLabs TTS (Arabic voice)
- **AI:** OpenAI GPT-4 (conversation)
- **Database:** Supabase PostgreSQL
- **Port:** 8080
- **Entry Point:** `agent.py`

#### Part 2: CallCenter (Audio Multi-Assistant Backend)

- **Language:** Python 3.11
- **Framework:** FastAPI + LiveKit Agents SDK
- **Audio Only:** No video (OpenAI STT/LLM/TTS)
- **Voice:** ElevenLabs TTS (Arabic voice)
- **AI:** OpenAI GPT-4 Turbo (3 personas)
- **Multi-Assistant:** Reception, Sales, Complaints
- **Routing:** Sentiment-based analysis
- **Database:** Supabase PostgreSQL
- **Port:** 8000 (API), Agent connects to LiveKit
- **Entry Points:** `main.py` (API), `call_center_agent.py` (Agent Worker)

#### Part 3: Frontend (Shared Web Interface)

- **Framework:** Next.js 14
- **Language:** TypeScript + React
- **UI:** Tailwind CSS
- **Real-time:** LiveKit React Components
- **Port:** 3000
- **Routes:**
  - `/avatar/*` → Video avatar calls
  - `/callcenter/*` → Audio call center

---

## 📚 Core Documentation

### Configuration & Setup

1. **[Configuration Analysis](./CALLCENTER_CONFIGURATION_ANALYSIS.md)**
   - How Avatary works (reference implementation)
   - What Call Center has vs what it needs
   - Environment configuration comparison
   - Multi-assistant system overview
   - **Key Finding:** Agent worker not being started

2. **[Implementation Guide](./CALLCENTER_IMPLEMENTATION_GUIDE.md)**
   - Quick start (test mode)
   - Production setup with Docker
   - Multi-assistant integration code
   - Testing procedures
   - Troubleshooting guide

3. **[Sentiment-Based Routing](./SENTIMENT_BASED_ROUTING.md)**
   - How sentiment analysis works
   - Routing logic: Excited → Sales, Complaining → Complaints
   - Implementation with OpenAI GPT-4
   - Testing examples
   - Monitoring & tuning

---

## 🎭 Multi-Assistant System

### Three AI Personas

#### 1. Reception Assistant - Ahmed (أحمد)
- **Role:** Friendly receptionist
- **Tone:** Welcoming, professional
- **Responsibilities:**
  - Greet customers
  - Collect basic information
  - Provide company info
  - Route to appropriate department
- **Language Support:** Arabic & English

#### 2. Sales Assistant - Sarah (سارة)
- **Role:** Enthusiastic sales representative
- **Tone:** Positive, persuasive
- **Responsibilities:**
  - Explain services
  - Handle objections
  - Provide quotes
  - Close deals
- **Trigger:** Positive sentiment (interested, wants to buy)

#### 3. Complaints Assistant - Mohammed (محمد)
- **Role:** Empathetic support specialist
- **Tone:** Understanding, solution-focused
- **Responsibilities:**
  - Listen to complaints
  - Show empathy
  - Propose solutions
  - Create support tickets
- **Trigger:** Negative sentiment (complaining, problem)

### Routing Flow

```
Customer joins call
     ↓
[Reception - Ahmed]
     ↓
Customer speaks
     ↓
Sentiment Analysis
     ↓
┌────────┴────────┐
│                 │
Excited/Buying?   Complaining?
│                 │
↓                 ↓
[Sales - Sarah]   [Complaints - Mohammed]
```

---

## 🔧 Key Technical Differences

### Avatary vs Call Center

| Feature | Avatary | Call Center |
|---------|---------|-------------|
| **Media Type** | Video + Audio | Audio Only |
| **Video Provider** | Tavus | None |
| **AI Assistants** | 1 (single agent) | 3 (multi-assistant) |
| **Routing** | None | Sentiment-based |
| **Startup** | Single process | Two processes (API + Agent) |
| **Use Case** | Premium video experience | Cost-effective support |
| **Cost** | ~$0.37/min | ~$0.05/min |

### Shared Infrastructure

Both systems use:
- ✅ Same LiveKit Cloud: `wss://tavus-agent-project-i82x78jc.livekit.cloud`
- ✅ Same OpenAI API key
- ✅ Same ElevenLabs voice (Arabic)
- ✅ Same Supabase database
- ✅ Same frontend (different routes)

**No conflicts - can run simultaneously!**

---

## 🚀 Quick Commands

### Development Mode

```bash
# Start Avatary (Video Avatar)
cd /var/www/avatar/avatary
python agent.py start

# Start Call Center API
cd /var/www/avatar/callCenter
python main.py

# Start Call Center Agent Worker
cd /var/www/avatar/callCenter
python call_center_agent.py

# Start Frontend
cd /var/www/avatar/frontend
npm run dev
```

### Docker Mode

```bash
# Start all services
docker-compose up

# Individual services
docker-compose up backend     # Avatary
docker-compose up callcenter  # Call Center API (needs agent worker too!)
docker-compose up frontend    # Frontend

# View logs
docker-compose logs -f callcenter
docker logs avatar-callcenter-agent -f
```

---

## 🐛 Troubleshooting

### Problem: Call Center agent doesn't join room

**Cause:** Agent worker (`call_center_agent.py`) not started

**Solution:**
```bash
# Start agent worker manually
cd /var/www/avatar/callCenter
python call_center_agent.py

# Or update Docker to start both processes
```

See: [Implementation Guide](./CALLCENTER_IMPLEMENTATION_GUIDE.md#production-setup-docker)

### Problem: No voice response

**Causes:**
- Missing OpenAI API key
- Missing ElevenLabs API key
- Agent not connected to LiveKit

**Solution:** Check `.env` configuration
See: [Configuration Analysis](./CALLCENTER_CONFIGURATION_ANALYSIS.md#configuration-comparison)

### Problem: Persona doesn't switch

**Cause:** Sentiment routing not implemented

**Solution:** Follow sentiment-based routing guide
See: [Sentiment-Based Routing](./SENTIMENT_BASED_ROUTING.md)

---

## 📊 Project Scan Report

Full project analysis state: [project-scan-report.json](./project-scan-report.json)

**Project Classification:**
- Repository Type: Multi-part (3 components)
- Primary Language: Python + TypeScript
- Architecture: Microservices (Backend 1, Backend 2, Frontend)
- Deployment: Docker Compose

---

## 📝 Implementation Checklist

### Avatary (Video Avatar) - ✅ Complete

- [x] LiveKit Agent Worker configured
- [x] Tavus integration working
- [x] ElevenLabs Arabic voice
- [x] Database integration
- [x] Frontend pages
- [x] Docker deployment

### Call Center (Audio Multi-Assistant) - ⚠️ In Progress

- [x] FastAPI server configured
- [x] API endpoints working
- [x] Token generation
- [x] CRM system
- [x] 3 personas defined (Reception, Sales, Complaints)
- [ ] **Agent worker auto-start** ← NEEDS IMPLEMENTATION
- [ ] **Sentiment-based routing** ← NEEDS IMPLEMENTATION
- [ ] **Multi-assistant switching** ← NEEDS IMPLEMENTATION

---

## 🎯 Next Steps

### Immediate Actions

1. **Start Agent Worker**
   - Implement dual-process startup (API + Agent)
   - Test voice interaction
   - Verify agent joins room automatically

2. **Integrate Sentiment Analysis**
   - Add `sentiment_analyzer.py` module
   - Update `call_center_agent.py` with routing logic
   - Test persona switching

3. **Test Full Flow**
   - Reception → Sales transition
   - Reception → Complaints transition
   - Verify smooth handoffs

### Future Enhancements

- [ ] Smart routing with conversation history
- [ ] CRM integration for persona context
- [ ] Analytics per assistant
- [ ] Multi-language support enhancements
- [ ] WebSocket real-time updates

---

## 📖 Additional Resources

### Existing Project Documentation

The project contains extensive existing documentation:

- **Root Documentation:** 54 markdown files
  - Call Center docs: 19 files (implementation, API, testing)
  - Docker docs: 9 files (deployment, setup)
  - LiveKit docs: 5 files (integration, setup)
  - System status and guides

- **Avatary Documentation:** 30 markdown files
  - Implementation guides
  - Feature documentation
  - Historical records

- **Architecture Documentation:**
  - [ARCHITECTURE_EXPLANATION.md](../ARCHITECTURE_EXPLANATION.md)
  - [AVATAR_VS_CALLCENTER_COMPARISON.md](../AVATAR_VS_CALLCENTER_COMPARISON.md)

### External References

- [LiveKit Documentation](https://docs.livekit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [ElevenLabs Documentation](https://docs.elevenlabs.io/)
- [Tavus API](https://docs.tavus.io/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🔐 Security & Credentials

**All credentials are configured and working:**

- ✅ LiveKit Cloud connection
- ✅ OpenAI API key
- ✅ ElevenLabs API key
- ✅ Tavus API key (for avatary)
- ✅ Supabase database credentials

**Note:** Credentials are stored in `.env` files (not committed to git)

---

## 📞 Support & Contact

For issues or questions:
1. Check troubleshooting sections in guides
2. Review existing documentation
3. Check logs: `/var/www/avatar/callCenter/logs/`

---

## 📄 Document Versions

| Document | Version | Date | Status |
|----------|---------|------|--------|
| Configuration Analysis | 1.0 | 2025-11-10 | ✅ Complete |
| Implementation Guide | 1.0 | 2025-11-10 | ✅ Complete |
| Sentiment-Based Routing | 1.0 | 2025-11-10 | ✅ Complete |
| This Index | 1.0 | 2025-11-10 | ✅ Complete |

---

## 🎉 Summary

**You have a multi-part AI communication system:**

1. **Avatary:** Working video avatar calls (premium experience)
2. **Call Center:** Audio-only with 3 AI assistants (cost-effective)
3. **Frontend:** Unified interface for both systems

**Call Center just needs:**
- Start the agent worker
- Integrate sentiment-based routing
- Test multi-assistant switching

**Everything else is ready to go!**

---

**Documentation Index Created:** 2025-11-10
**Project:** Ornina AI Avatar & Call Center
**Status:** ✅ Documentation Complete
