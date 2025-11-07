# Master Plan - Ornina AI Avatar System

**Project**: Professional Interactive AI Avatar Call Center
**Company**: Ornina - AI Services & Digital Solutions (Damascus, Syria)
**Language**: Arabic (Syrian dialect)
**Status**: In Development

---

## Project Overview

Building a professional AI-powered call center system with:
- Voice avatar (Tavus video integration)
- Real-time Arabic conversation
- Knowledge base search
- Conversation tracking and analytics
- User information extraction

---

## Current Status (Latest Session - 2025-11-05)

### ✅ Completed

1. **Professional Conversation Management**
   - Created `ProfessionalConversationManager` class
   - Local message buffering (no lag during calls)
   - Save to database when call ends
   - Conversation records with metadata

2. **Database Schema**
   - `conversations` table for tracking calls
   - `messages` table for all conversation messages
   - `users` table for customer information
   - Knowledge base tables (products, services, training, FAQs)

3. **Fixed Agent Behavior**
   - Agent now answers from prompts.py first (no unnecessary database calls)
   - Tools only used for specific details (prices, dates)
   - Clear priority system in prompts

4. **TTS/Voice System**
   - Switched from ElevenLabs to OpenAI TTS (more reliable)
   - Voice: OpenAI Alloy (supports Arabic)
   - STT: OpenAI Whisper (Arabic)

---

## Architecture

```
User (Voice)
    ↓
LiveKit Room
    ↓
Agent (Python)
    ├→ OpenAI STT (Arabic speech-to-text)
    ├→ OpenAI LLM (gpt-4o-mini)
    ├→ Knowledge Base Tools (MCP)
    ├→ OpenAI TTS (text-to-speech)
    └→ Tavus Video Avatar
    ↓
Supabase Database
    ├→ conversations (call records)
    ├→ messages (all chat history)
    ├→ users (customer info)
    └→ knowledge_base (products, services, FAQs)
```

---

## System Flow

### Call Start
1. User connects to LiveKit room
2. Agent creates conversation record in database
3. Tavus video avatar initializes
4. Agent greets user in Arabic

### During Call
1. User speaks → OpenAI STT transcribes
2. Agent checks prompts.py for answer
3. If not found → searches knowledge base
4. LLM generates response
5. OpenAI TTS converts to speech
6. **Messages buffered locally** (fast, no database lag)
7. User info extracted automatically (name, phone)

### Call End
1. User disconnects
2. **All buffered messages saved to database**
3. Conversation record updated (duration, status, user info)
4. Local backup created in /tmp/
5. User info saved to users table

---

## Technologies

### Core
- **LiveKit Agents**: Real-time voice/video framework
- **Python 3.12**: Main programming language
- **Supabase**: PostgreSQL database with real-time features

### AI Services
- **OpenAI GPT-4o-mini**: Conversational AI
- **OpenAI Whisper**: Arabic speech-to-text
- **OpenAI TTS (Alloy)**: Text-to-speech (Arabic)
- **Tavus**: Video avatar service

### Tools & Libraries
- **MCP (Model Context Protocol)**: Function calling for knowledge base
- **Silero VAD**: Voice activity detection
- **dotenv**: Environment configuration

---

## File Structure

```
/var/www/avatar /avatary/
├── agent.py                              # Main agent (ACTIVE)
├── prompts.py                            # Agent instructions & knowledge
├── professional_conversation_manager.py   # Conversation tracking system
├── conversation_logger.py                # Legacy message logging
├── users_manager.py                      # User data management
├── knowledge_base_manager.py             # Database search
├── local_mcp_server.py                   # MCP tools definition
├── create_conversations_table.sql        # Database schema
├── create_ornina_complete_database.sql   # Knowledge base schema
├── .env                                  # API keys & config
├── docs/                                 # Current documentation
│   ├── MASTER_PLAN.md                   # This file
│   ├── WHAT_WE_DID.md                   # Completed work log
│   ├── TODO.md                          # Remaining tasks
│   ├── COMPLETE_FIX_GUIDE.md            # Latest fixes guide
│   ├── OFFICIAL_LIVEKIT_LOGGING.md      # Conversation logging docs
│   └── PROFESSIONAL_SYSTEM_UPGRADE.md   # System upgrade guide
└── history/                              # Old/outdated documentation
    └── [15 old MD files]
```

---

## Key Components

### 1. Agent (agent.py)
- Main entry point
- Handles LiveKit connection
- Manages conversation flow
- Integrates all services

### 2. Prompts (prompts.py)
- Agent personality and behavior
- Company information (Ornina)
- 6 services descriptions
- 6 training programs
- Conversation flow guidelines

### 3. Professional Manager (professional_conversation_manager.py)
- Creates conversation records
- Buffers messages locally
- Saves to database on call end
- Manages conversation lifecycle

### 4. Knowledge Base (knowledge_base_manager.py)
- Searches products/services
- Searches training programs
- Searches FAQs
- Smart search across all tables

### 5. MCP Tools (local_mcp_server.py)
- search_knowledge_base
- get_all_products
- get_all_training_programs
- get_company_contact

---

## Database Schema

### conversations
- conversation_id (unique)
- room_name
- participant_identity
- started_at, ended_at, duration_seconds
- status (active/completed/abandoned)
- user_name, user_phone, user_email
- summary
- message_count
- language

### messages
- message_id (unique)
- conversation_id (FK to conversations)
- role (user/assistant)
- content
- timestamp
- room_name
- user_phone
- metadata (JSON)

### users
- user_id
- name, phone, email
- created_at, updated_at

### Knowledge Base Tables
- products (6 services)
- training_programs (6 courses)
- faqs (Q&A pairs)
- work_areas (28 service areas)
- target_markets (6 market segments)
- company_info (contact details)

---

## API Keys Required

```env
# OpenAI (ACTIVE - Currently Used)
OPENAI_API_KEY=sk-...

# Supabase (ACTIVE)
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...

# LiveKit (ACTIVE)
LIVEKIT_URL=wss://...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...

# Tavus (ACTIVE)
TAVUS_API_KEY=...
TAVUS_PERSONA_ID=...
TAVUS_REPLICA_ID=...

# ElevenLabs (DISABLED - Had connection issues)
# ELEVENLABS_API_KEY=...
# ELEVENLABS_VOICE_ID=...
```

---

## Known Issues & Solutions

### Issue 1: ElevenLabs TTS Connection Failures
**Status**: ❌ Disabled
**Solution**: Switched to OpenAI TTS (more reliable)
**Future**: Can re-enable once API key/connection is fixed

### Issue 2: Agent Called Database Unnecessarily
**Status**: ✅ Fixed
**Solution**: Updated tool descriptions and prompts.py with clear priorities

### Issue 3: Conversation Records Missing
**Status**: ✅ Fixed
**Solution**: Implemented ProfessionalConversationManager

### Issue 4: Lag During Calls
**Status**: ✅ Fixed
**Solution**: Local message buffering, save to database only on call end

---

## Next Steps

See `docs/TODO.md` for detailed task list.

**Immediate**:
1. Test with OpenAI TTS (verify sound works)
2. Create conversations table in Supabase
3. Test complete conversation flow
4. Verify messages and conversations saved correctly

**Short-term**:
1. Test knowledge base search
2. Add more FAQs to database
3. Improve user info extraction
4. Add conversation analytics

**Long-term**:
1. Frontend dashboard for viewing conversations
2. Real-time conversation monitoring
3. Sentiment analysis
4. Performance optimization
5. Multi-language support (beyond Arabic)

---

## Testing Checklist

- [ ] Agent starts without errors
- [ ] Sound works (OpenAI TTS)
- [ ] User speech recognized (Arabic)
- [ ] Agent responds correctly
- [ ] Messages buffered during call
- [ ] Conversations table has records
- [ ] Messages saved when call ends
- [ ] User info extracted (if provided)
- [ ] Knowledge base search works
- [ ] Video avatar displays (Tavus)

---

## Performance Targets

- **Response Time**: < 2 seconds
- **Uptime**: > 99%
- **Conversation Save**: 100% success rate
- **User Info Extraction**: > 80% accuracy
- **Knowledge Base Search**: < 500ms

---

## Contact & Resources

**Documentation**: `/var/www/avatar /avatary/docs/`
**History**: `/var/www/avatar /avatary/history/`
**LiveKit Docs**: https://docs.livekit.io/agents/
**Supabase Docs**: https://supabase.com/docs
**OpenAI Docs**: https://platform.openai.com/docs

---

## Version History

- **v0.3** (2025-11-05): Professional conversation management, OpenAI TTS
- **v0.2** (2025-11-04): Knowledge base integration
- **v0.1** (2025-11-03): Initial agent setup

---

*Last Updated: 2025-11-05 15:45 UTC*
