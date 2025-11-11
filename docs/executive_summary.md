# Executive Summary - Avatar Agent Codebase Analysis

## Quick Facts

| Aspect | Details |
|--------|---------|
| **Framework** | LiveKit Agents 1.0 (not OpenAI Assistants) |
| **LLM Model** | gpt-4o-mini (via OpenAI) |
| **Code Status** | Production-ready, well-structured |
| **Language** | Arabic + English (bilingual) |
| **Persistence** | Supabase (conversations saved on call end) |
| **Vision Integration** | GPT-4 Vision (every 3 seconds) |
| **Face Recognition** | InsightFace (optional, for minister greetings) |
| **Total Files Analyzed** | 15+ core files, ~2000+ lines of agent code |

---

## Key Findings

### 1. **Assistants API NOT Currently Used**
- OpenAI SDK is installed but only used for Vision API
- Chat completions are made directly via LiveKit plugin
- No threads, no persistent conversation memory in API
- Conversations saved to Supabase after call ends

### 2. **Agent Structure is Custom**
- Extends LiveKit's `Agent` class
- Overrides `llm_node()` method for context injection
- Uses Pydantic models for type-safe context
- Tools registered as Python async functions

### 3. **Visual Context is Injected Per-Call**
- Vision processor analyzes video every 3 seconds
- Updates Pydantic model with fresh analysis
- System message injected before each LLM call
- Context expires after 15 seconds

### 4. **Conversation Persistence is Two-Tier**
- **During call**: Messages buffered in memory (fast, no lag)
- **At call end**: Batch saved to Supabase database
- Professional manager handles both tiers
- User info extracted and saved separately

### 5. **Tool System is MCP-Style**
- 4 knowledge base tools defined in local_mcp_server.py
- Tools converted from JSON schema to Python functions
- Decorated with LiveKit's @function_tool()
- Calls local kb_manager for search

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  LiveKit Agent Session (Real-time voice/video I/O)      │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ VisualAwareAgent (Custom Agent)                   │   │
│  │ - instructions: from prompts.py                   │   │
│  │ - visual_store: Pydantic VisualContextStore       │   │
│  │ - _tools: List of decorated tool functions        │   │
│  │ - llm_node() override: injects context            │   │
│  └───────────────────────────────────────────────────┘   │
│                       ↕                                   │
│  ┌──────────────────────────────┐                        │
│  │ OpenAI Chat Completions API  │ (gpt-4o-mini)         │
│  └──────────────────────────────┘                        │
│         ↕             ↕             ↕                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐              │
│  │ STT      │  │ LLM      │  │ TTS       │              │
│  │ (Arabic) │  │ (Chat)   │  │ (Alloy)   │              │
│  └──────────┘  └──────────┘  └───────────┘              │
└─────────────────────────────────────────────────────────┘
         ↕                                           
┌─────────────────────────────────────────────────────────┐
│  Parallel Services                                      │
│                                                         │
│  ┌──────────────────┐      ┌─────────────────────┐    │
│  │ Vision Processor │      │ Conversation Manager │    │
│  │                  │      │                      │    │
│  │ - GPT-4 Vision   │      │ - Event listener     │    │
│  │ - Every 3 secs   │      │ - Local buffering    │    │
│  │ - Face recognition │   │ - Supabase saving    │    │
│  │ - Context inject │      │                      │    │
│  └──────────────────┘      └─────────────────────┘    │
└─────────────────────────────────────────────────────────┘
        ↕                              ↕
   ┌─────────┐                    ┌──────────┐
   │ Tools   │                    │ Database │
   │ Search  │                    │ Supabase │
   │ Local   │                    └──────────┘
   │ KB      │
   └─────────┘
```

---

## Current System Strengths

1. **Low Latency**: Direct LLM calls, no polling overhead
2. **Clean Architecture**: Well-separated concerns, type-safe
3. **Flexible Context**: Can inject any context before LLM call
4. **Professional Persistence**: Two-tier buffering avoids lag
5. **Vision Integration**: Real-time visual awareness built-in
6. **Bilingual**: Arabic-first design with English support
7. **Tool Support**: Knowledge base accessible via tool calls

---

## Current System Limitations

1. **No API-Level Persistence**: Context lost if call interrupted
2. **No File Storage**: Can't attach files to assistant
3. **No Conversation Resumption**: Can't resume interrupted calls
4. **Context Window Limited**: All context must fit in single prompt
5. **No Vector Search**: Can't leverage knowledge embeddings
6. **No Session Memory**: Each new room starts fresh
7. **Polling Not Available**: Can't check for new info proactively

---

## If You Want to Use OpenAI Assistants API

### Required Changes (High Level)

1. **Create Thread per Conversation**
   ```python
   thread = client.beta.threads.create()
   thread_id = thread.id
   # Persist thread_id with conversation
   ```

2. **Create Assistant Configuration**
   ```python
   assistant = client.beta.assistants.create(
       name="Ornina Reception",
       instructions=AGENT_INSTRUCTIONS,
       model="gpt-4o-mini",
       tools=[...]  # Tool definitions
   )
   ```

3. **Replace LLM Call Flow**
   - Instead of: `llm = openai.LLM()`
   - Use: `client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)`
   - Poll: `run = client.beta.threads.runs.retrieve(thread_id, run_id)`
   - Submit tool outputs: `client.beta.threads.runs.submit_tool_outputs(...)`

4. **Handle Tool Results Differently**
   - Instead of: Synchronous tool call with return value
   - Use: `requires_action` run status → submit results back

5. **Manage Visual Context**
   - Option A: Inject as user message in thread
   - Option B: Upload as file attachment
   - Option C: Use system message during run creation

### Effort Required
- **Estimated Work**: 3-5 days for complete migration
- **New Files**: 3-4 new modules
- **Testing**: Moderate (run polling adds complexity)
- **Risk**: Medium (adds latency from polling)

---

## Comparison: Keep Current vs Switch to Assistants

### Keep Current LiveKit System
**Pros:**
- Proven, production-ready
- Low latency, no polling
- Flexible context injection
- Great for real-time interactions
- Simple tool execution

**Cons:**
- No persistent conversation memory
- Context lost if interrupted
- Can't resume calls
- Limited by context window
- No vector search

### Switch to Assistants API
**Pros:**
- Persistent conversation history
- Can resume interrupted calls
- File attachment support
- Built-in memory management
- Conversation threads for organization

**Cons:**
- Higher latency (polling overhead)
- More complex implementation
- Extra API calls (costs more)
- Less control over execution flow
- Visual context handling less elegant

### Recommendation
**Keep current system if:**
- Calls rarely exceed context window
- Interruptions are not a concern
- You need the fastest possible response
- Visual context is important

**Switch to Assistants if:**
- You need conversation resumption
- Calls are frequently interrupted
- You want persistent memory
- File attachments are required
- You can accept slight latency increase

**Hybrid approach (Best):**
- Keep LiveKit for voice/video I/O
- Use Assistants API as backend for conversation memory
- Inject visual context as messages
- Get best of both worlds

---

## File Locations & Key Code

### Core Agent Files
- **Main entrypoint**: `/var/www/avatar/avatary/agent.py` (line 103)
- **Custom agent class**: `/var/www/avatar/avatary/visual_aware_agent.py`
- **Instructions**: `/var/www/avatar/avatary/prompts.py` (AGENT_INSTRUCTIONS)
- **Context models**: `/var/www/avatar/avatary/visual_context_models.py`

### Vision & Tools
- **Vision processor**: `/var/www/avatar/avatary/vision_processor.py` (line 72+)
- **Tool definitions**: `/var/www/avatar/avatary/local_mcp_server.py` (line 11+)
- **Tool registration**: `/var/www/avatar/avatary/agent.py` (line 258+)

### Persistence
- **Conversation manager**: `/var/www/avatar/avatary/professional_conversation_manager.py`
- **Event listener**: `/var/www/avatar/avatary/agent.py` (line 391+)
- **Shutdown callback**: `/var/www/avatar/avatary/agent.py` (line 417+)

### Call Center
- **Personas**: `/var/www/avatar/callCenter/openai_personas.py`
- **Call center agent**: `/var/www/avatar/callCenter/call_center_agent.py`

---

## Critical Code Sections

### 1. Context Injection (14 lines of logic)
`visual_aware_agent.py`, lines 35-71:
- Gets fresh visual context
- Checks if fresh (< 15 seconds)
- Injects as system message
- Delegates to default LLM handler

### 2. Tool Registration (65 lines)
`agent.py`, lines 258-322:
- Gets tool definitions from local_mcp_server
- Converts JSON schema to Python function signatures
- Creates async tool functions with closure
- Decorates with @function_tool()
- Registers on agent._tools list

### 3. Message Events (25 lines)
`agent.py`, lines 391-415:
- Listens to conversation_item_added events
- Saves message immediately
- Buffers to local transcript
- Persisted on call end

### 4. Vision Processing (30 lines)
`vision_processor.py`, lines 72-125:
- Sends JPEG to GPT-4 Vision
- Gets analysis
- Calls callback with results

---

## Next Steps Recommendation

### Phase 1: Understand Current System (Done!)
- Codebase explored
- Architecture documented
- Key patterns identified

### Phase 2: Make a Decision
- Do you need conversation resumption?
- Is latency critical?
- Are file attachments needed?

### Phase 3: If Keeping Current System
- Document the context injection pattern
- Add conversation export feature
- Implement context windowing for long calls
- Consider caching visual context updates

### Phase 4: If Switching to Assistants
- Create proof-of-concept with thread management
- Benchmark latency vs current system
- Implement tool executor for Assistants API
- Create feature flag for gradual migration
- Test conversation persistence and resumption

---

## Resources Provided

Three detailed documents have been created:

1. **codebase_analysis.md** (12 sections)
   - High-level architecture overview
   - Current implementation details
   - OpenAI integration analysis
   - Migration requirements and comparison

2. **technical_deep_dive.md** (12 sections)
   - Code-level implementation details
   - Line-by-line flow analysis
   - Specific function signatures
   - Integration points and patterns

3. **executive_summary.md** (this file)
   - Quick reference facts
   - Key findings
   - Architecture diagram
   - Recommendations

---

## Questions Answered

**Q: Is the system currently using OpenAI Assistants API?**
A: No. It uses LiveKit Agents 1.0 with direct OpenAI API calls.

**Q: How is visual context integrated?**
A: GPT-4 Vision analyzes frames every 3 seconds, results injected as system message before each LLM call.

**Q: How are conversations persisted?**
A: Two-tier: buffered in memory during call, saved to Supabase on call end.

**Q: What tools are available?**
A: 4 knowledge base search tools defined in local_mcp_server.py, registered as Python async functions.

**Q: Can conversations be resumed?**
A: Currently no - each new room starts fresh. Assistants API would enable this.

**Q: What's the current architecture for handling sessions?**
A: LiveKit manages STT/LLM/TTS, custom VisualAwareAgent injects context, Pydantic models for type safety.

**Q: What would migration to Assistants API require?**
A: Thread creation, Assistant configuration, tool executor, run polling, and visual context handling via messages.

---

## Conclusion

The Avatar system is well-designed with a professional architecture that handles voice, video, vision, and tool integration elegantly. The current approach of using LiveKit Agents 1.0 with custom context injection is excellent for real-time interactions.

OpenAI Assistants API would add persistent conversation memory and resumption capabilities, but at the cost of additional latency from polling. The decision to migrate should be based on:
- Whether conversation resumption is needed
- Tolerance for polling latency
- Need for file attachments
- Trade-off between simplicity and features

A hybrid approach using both systems might provide the best balance.

