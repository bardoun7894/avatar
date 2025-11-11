# Avatar Codebase Analysis - Current Agent Implementation

## Executive Summary

The Avatar system uses **LiveKit Agents 1.0 framework** with a custom **VisualAwareAgent** implementation. It does NOT currently use OpenAI Assistants API (beta). The system uses direct LLM calls through the LiveKit plugin system with context injection. 

**Key Finding**: OpenAI SDK is installed (with Assistant API support) but is NOT being used - only the basic chat completion API is used through LiveKit's openai plugin.

---

## 1. Current Agent Architecture

### Framework Stack
- **Primary Framework**: LiveKit Agents 1.0 (not OpenAI Assistants)
- **LLM Backend**: OpenAI (via livekit-plugins-openai)
- **Model**: gpt-4o-mini
- **STT**: OpenAI (Arabic language)
- **TTS**: OpenAI (Alloy voice, supports Arabic)
- **VAD**: Silero (Voice Activity Detection)

### Core Files Structure
```
avatary/
├── agent.py                           # Main entrypoint (340+ lines)
├── prompts.py                         # Agent instructions (195 lines)
├── visual_aware_agent.py              # Custom agent with vision injection
├── visual_context_models.py           # Pydantic models for context
├── vision_processor.py                # GPT-4 Vision integration
├── professional_conversation_manager.py # Conversation persistence
├── local_mcp_server.py                # Knowledge base tools
└── requirements.txt                   # Dependencies (24 packages)

callCenter/
├── call_center_agent.py               # Call center variant
├── openai_personas.py                 # 3 persona configurations
└── requirements.txt
```

---

## 2. How the Current Agent Works

### 2.1 Agent Structure

The agent implements a **custom inheritance pattern**:

```python
class VisualAwareAgent(Agent):
    """Overrides llm_node to inject visual context before LLM calls"""
    
    def __init__(self, instructions: str, visual_store: VisualContextStore):
        super().__init__(instructions=instructions)
        self.visual_store = visual_store
        self._base_instructions = instructions
```

**Key Pattern**: LiveKit Agents 1.0 allows overriding the `llm_node()` method to intercept LLM calls.

### 2.2 How Context Injection Works

**File**: `avatary/visual_aware_agent.py` (lines 35-71)

```python
async def llm_node(
    self,
    chat_ctx: llm.ChatContext,
    tools: list[llm.FunctionTool],
    model_settings: Any,
) -> AsyncIterable[llm.ChatChunk]:
    # 1. Get current visual analysis from Pydantic store
    current_visual = self.visual_store.get_current()
    
    if current_visual:
        # 2. Inject as system message BEFORE LLM call
        visual_message = current_visual.to_injection_text()
        chat_ctx.add_message(role="system", content=visual_message)
    
    # 3. Delegate to default LLM processing
    async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
        yield chunk
```

**How It Differs from Assistants API**:
- No thread-based conversation persistence
- No file storage capability
- Context is injected per-call, not stored permanently
- Tools are registered on the agent instance

### 2.3 Session Initialization

**File**: `avatary/agent.py` (lines 198-241)

```python
# 1. Create LLM
session_config["llm"] = openai.LLM(model="gpt-4o-mini")

# 2. Create TTS (OpenAI Alloy voice)
session_config["tts"] = openai.TTS(voice="alloy", speed=1.0)

# 3. Create STT (Arabic)
session_config["stt"] = openai.STT(language="ar")

# 4. Create Visual Context Store (Pydantic-based)
visual_store = VisualContextStore(
    enabled=True,
    max_age_seconds=15.0
)

# 5. Create Custom Agent
agent = VisualAwareAgent(
    instructions=AGENT_INSTRUCTIONS,
    visual_store=visual_store
)

# 6. Start session
await session.start(
    room=ctx.room,
    agent=agent,
    room_input_options=RoomInputOptions(noise_cancellation=...),
)
```

---

## 3. OpenAI Integration Analysis

### 3.1 Current OpenAI Usage

**What IS Used**:
- ✅ Chat Completions API (via `openai.LLM()`)
- ✅ TTS API (via `openai.TTS()`)
- ✅ STT API (via `openai.STT()`)
- ✅ Vision API (via `AsyncOpenAI()` in `vision_processor.py`)

**What IS NOT Used**:
- ❌ Assistants API (beta)
- ❌ Threads
- ❌ File storage
- ❌ Vector store
- ❌ Knowledge retrieval

### 3.2 OpenAI SDK Installation

The codebase HAS the full OpenAI SDK installed (evidenced by the grep results showing assistant-related files), but it's **not being utilized**.

**In `vision_processor.py` (line 21)**:
```python
self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Used for GPT-4 Vision only, not Assistants
```

### 3.3 Call Center Personas

**File**: `callCenter/openai_personas.py` (310 lines)

Defines 3 personas using **basic system prompts** (not Assistant API):
1. **RECEPTION_PERSONA** - "Ahmed" - Greeting & routing
2. **SALES_PERSONA** - "Sarah" - Selling services
3. **COMPLAINTS_PERSONA** - "Mohammed" - Support & issues

These are just Pydantic models with system prompts - not using Assistants API.

---

## 4. Tool Integration (MCP-style)

### 4.1 Knowledge Base Tools

**File**: `avatary/local_mcp_server.py` (lines 10-52)

Defines 4 tools:
1. `search_knowledge_base` - Search company info
2. `get_all_products` - List services
3. `get_all_training_programs` - List training
4. `get_company_contact` - Get address/phone

**Tool Registration** (agent.py, lines 258-320):

```python
# Get tools
local_tools = get_local_tools()

# Create decorated functions from JSON schema
for tool in local_tools:
    tool_name = tool["name"]
    tool_schema = tool["inputSchema"]
    
    # Build function signature from schema
    def make_tool_fn(name, desc, sig_params, annots):
        async def tool_fn(**kwargs):
            result = call_tool(name, kwargs)
            return json.dumps(result)
        # ... signature setup
        return tool_fn
    
    func = make_tool_fn(...)
    decorated_func = function_tool()(func)
    tools.append(decorated_func)

# Register with agent
agent._tools.extend(tools)
```

**How Different from Assistants API**:
- Functions are registered directly on agent instance
- No file attachment support
- No persistent tool definitions across sessions
- Tools are Python functions, not JSON schemas in API

---

## 5. Visual Context & Session Management

### 5.1 Visual Context Store

**File**: `avatary/visual_context_models.py` (99 lines)

Uses **Pydantic** for type-safe context:

```python
class VisualContextStore(BaseModel):
    latest_analysis: Optional[VisualAnalysis] = None
    enabled: bool = True
    max_age_seconds: float = 15.0  # Context expires after 15 seconds
    
    def get_current(self) -> Optional[VisualAnalysis]:
        if not self.enabled or not self.latest_analysis:
            return None
        
        if self.latest_analysis.age_seconds > self.max_age_seconds:
            return None
        
        return self.latest_analysis
```

### 5.2 Vision Processing

**File**: `avatary/vision_processor.py` (200+ lines)

Continuous loop:
1. Capture frame from user's camera
2. Send to GPT-4 Vision API
3. Get analysis (professional exhibition context)
4. Update VisualContextStore
5. Trigger callback `handle_visual_update()`

```python
async def start_continuous_analysis(
    self,
    video_track: rtc.RemoteVideoTrack,
    callback: Callable
):
    """Continuous vision analysis every 3 seconds"""
    while self.is_running:
        frame = await self.capture_frame_from_track(video_track)
        if frame:
            analysis = await self.analyze_image(frame)
            if callback and analysis:
                await callback(analysis, frame)
        await asyncio.sleep(self.analysis_interval)
```

### 5.3 Face Recognition Integration

**Optional Feature**: InsightFace integration for minister recognition

- File: `avatary/insightface_recognition.py`
- Lazy-loads face recognizer
- Returns matched person if confidence > threshold
- Used to personalize greetings

---

## 6. Conversation Persistence

### 6.1 Professional Conversation Manager

**File**: `avatary/professional_conversation_manager.py` (200+ lines)

Two-tier persistence:
1. **Local Buffering** (fast, no lag):
   - Messages buffered in memory during call
   - Method: `add_message_to_local_transcript()`

2. **Database Persistence** (on call end):
   - Saves conversation to Supabase when call ends
   - Method: `end_conversation()`
   - Saves to tables: `conversations`, `conversation_messages`, `users`

```python
def start_conversation(self, conversation_id, room_name, participant_identity):
    """Create conversation record in database"""
    # ... creates record in conversations table

def add_message_to_local_transcript(self, role, content):
    """Buffer message locally (fast)"""
    self.local_transcript.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    })

def end_conversation(self, user_name=None, user_phone=None):
    """Save buffered transcript to database"""
    # ... inserts all messages to conversation_messages table
```

### 6.2 Event Listener Pattern

**File**: `avatary/agent.py` (lines 391-415)

LiveKit's official pattern:

```python
@session.on("conversation_item_added")
def on_conversation_item_added(event: ConversationItemAddedEvent):
    """Automatic event fired by LiveKit for every message"""
    role = event.item.role  # "user" or "assistant"
    content = event.item.text_content
    
    if content and content.strip():
        # 1. Save to database immediately
        save_message(role=role, content=content)
        
        # 2. Buffer locally
        prof_manager.add_message_to_local_transcript(
            role=role,
            content=content,
        )
```

---

## 7. Agent Instructions & Prompts

### 7.1 Base Instructions

**File**: `avatary/prompts.py` (195 lines)

**Format**: System prompt with:
- Company info (address, phone, social media)
- 6 Services described in detail
- 6 Training programs described
- Conversation flow (7 steps)
- Tool usage guidelines
- Conversation tips

**Language**: Arabic-first (Egyptian dialect), with English context

**Key Instruction**:
```
1. أولاً وأخيراً: اجب دائماً من المعلومات الموجودة أعلاه في هذا الملف
(ALWAYS answer from the information in THIS file first!)

2. لا تستخدم قاعدة البيانات أبداً لهذه الأسئلة
(DO NOT use database for basic info - it's already in the prompt!)

3. استخدم قاعدة البيانات فقط لأسئلة محددة جداً
(Only use database for specific questions not in the prompt)
```

### 7.2 Call Center Personas

**File**: `callCenter/openai_personas.py` (310 lines)

3 distinct personas with different system prompts:

1. **RECEPTION** - "Ahmed"
   - Greeting, basic info, routing
   - Tone: Friendly, helpful, professional
   - Language: Arabic/English mixed

2. **SALES** - "Sarah"
   - Detailed service explanation
   - Tone: Enthusiastic, persuasive
   - Focus: Moving to purchase

3. **COMPLAINTS** - "Mohammed"
   - Problem-solving, empathy
   - Tone: Empathetic, professional
   - Focus: Resolution & follow-up

---

## 8. Current Workflow Flow

### 8.1 Session Lifecycle

```
1. ENTRYPOINT CALLED
   ├─ Load environment variables
   ├─ Initialize LLM (gpt-4o-mini)
   ├─ Initialize TTS (OpenAI Alloy)
   ├─ Initialize STT (OpenAI Arabic)
   ├─ Create VisualContextStore (Pydantic)
   └─ Create VisualAwareAgent

2. SESSION STARTED
   ├─ Subscribe to conversation_item_added events
   ├─ Register knowledge base tools (4 tools)
   ├─ Start video monitoring async task
   ├─ Start vision processing if camera found
   └─ Agent ready for conversation

3. CONVERSATION LOOP
   ├─ User speaks → STT captures text
   ├─ event: conversation_item_added (user message)
   │  └─ Save to database & buffer locally
   ├─ Vision processor (every 3s): GPT-4 Vision → analysis
   │  └─ Update VisualContextStore
   ├─ When agent generates response:
   │  └─ llm_node() called:
   │     ├─ Get fresh visual context
   │     ├─ Inject as system message
   │     ├─ Call LLM with full context
   │     └─ Return response
   ├─ TTS speaks response
   └─ Repeat

4. CALL ENDED
   ├─ Save final conversation to database
   ├─ Extract & save user info
   └─ Close database connections
```

### 8.2 Tool Call Flow

```
Agent Response Generation → LLM suggests tool call
                        ↓
                    Tool Decorator recognizes function call
                        ↓
                    Python async function executes
                        ↓
                    call_tool(tool_name, arguments)
                        ↓
                    kb_manager.smart_search(query)
                        ↓
                    Return JSON result
                        ↓
                    LLM receives tool result
                        ↓
                    Generate final response with tool data
```

---

## 9. What's Needed to Switch to OpenAI Assistants API

### 9.1 Major Changes Required

#### A. Thread Management (Currently: Missing)
```
CURRENT:
- No persistent conversation thread
- Context reset between calls (except visual store)
- Messages stored in local transcript only

NEEDED:
- Create thread per conversation
- Use thread_id for all requests
- Messages persisted in Assistants API
```

#### B. Assistant Configuration (Currently: Inline in prompts)
```
CURRENT:
- Instructions in prompts.py (system prompt)
- Tools in local_mcp_server.py (Python functions)
- Files: none

NEEDED:
- Create Assistant with instructions
- Upload files to Assistant
- Define tools via JSON schema
- Use assistant_id for all requests
```

#### C. Message Persistence (Currently: Dual-tier)
```
CURRENT:
- Live: Local transcript buffer
- Persistent: Supabase (on call end)
- No Assistants API storage

NEEDED:
- All messages in Threads (Assistants API)
- Optional: Also in Supabase for analytics
- Use run_id for tracking
```

#### D. Tool Execution (Currently: Python functions)
```
CURRENT:
- Tools decorated with @function_tool()
- Executed as Python async functions
- Results returned to LLM

NEEDED:
- Define tools in Assistants API (JSON schema)
- Implement tool result callback
- Create tool executor that calls Python functions
- Return results via tool_output_submission
```

#### E. Context Injection (Currently: llm_node override)
```
CURRENT:
- Visual context injected as system message
- Before each LLM call via llm_node()

NEEDED:
- Option 1: Inject as user message with visual context
- Option 2: Create system message in thread
- Option 3: Use file attachments for context
```

### 9.2 Architecture Change Required

```
CURRENT ARCHITECTURE:
┌─────────────────────────────────────────────────────────┐
│  LiveKit Agent Session                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ VisualAwareAgent (Custom Agent)                  │   │
│  │ ├─ instructions: str                             │   │
│  │ ├─ visual_store: VisualContextStore (Pydantic)   │   │
│  │ ├─ _tools: List[FunctionTool]                    │   │
│  │ └─ llm_node() override                           │   │
│  │    ├─ Get visual context                         │   │
│  │    ├─ Inject as system message                   │   │
│  │    └─ Call Agent.default.llm_node()              │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ↓                                 │
│         ┌───────────────────────────────┐                 │
│         │ OpenAI SDK (Chat Completions) │                 │
│         │ - models.chat.completions.create() │            │
│         └───────────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘


PROPOSED ARCHITECTURE (with Assistants API):
┌──────────────────────────────────────────────────────────────┐
│  LiveKit Agent Session                                       │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ AssistantAwareAgent (New Custom Agent)                │   │
│  │ ├─ assistant_id: str                                  │   │
│  │ ├─ thread_id: str (per conversation)                  │   │
│  │ ├─ visual_store: VisualContextStore (Pydantic)        │   │
│  │ ├─ tool_executors: Dict[str, Callable]                │   │
│  │ └─ llm_node() override                                │   │
│  │    ├─ Add visual context to thread as user message    │   │
│  │    ├─ Create run with thread_id                       │   │
│  │    ├─ Poll run status                                 │   │
│  │    ├─ If tool_call: Execute & submit result           │   │
│  │    └─ Return final response                           │   │
│  └───────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ↓                                    │
│     ┌──────────────────────────────────┐                     │
│     │ OpenAI Assistants API (Beta)      │                    │
│     │ - assistants.create()             │                    │
│     │ - threads.create()                │                    │
│     │ - threads.messages.create()       │                    │
│     │ - runs.create()                   │                    │
│     │ - runs.submit_tool_outputs()      │                    │
│     └──────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

### 9.3 File Structure Changes

```
CURRENT:
avatary/
├── agent.py (entrypoint)
├── prompts.py (system prompt string)
├── visual_aware_agent.py (custom agent class)
└── local_mcp_server.py (tool definitions as Python dicts)

PROPOSED:
avatary/
├── agent_v2.py (new entrypoint with Assistants)
├── assistant_aware_agent.py (new custom agent)
├── assistant_config.py (Assistant creation & setup)
├── assistant_tool_executor.py (tool execution for Assistants API)
├── prompts_v2.py (system prompt + Assistant files)
└── local_mcp_server.py (unchanged - tools as Python functions)
```

### 9.4 Dependency Changes

```
CURRENT:
- livekit-agents
- livekit-plugins-openai
- openai (SDK) - installed but not used for Assistants

NEW:
- livekit-agents (same)
- livekit-plugins-openai (same, for STT/TTS)
- openai (SDK) - NOW used for Assistants API!
  ├─ client.beta.assistants.create()
  ├─ client.beta.threads.create()
  ├─ client.beta.threads.runs.create()
  └─ client.beta.threads.runs.submit_tool_outputs()
```

---

## 10. Key Advantages of Current System

### What Works Well
1. **Low Latency**: No thread polling overhead
2. **Simple Context Injection**: Visual context injected as system message
3. **Direct Tool Calls**: Python functions, no API round-trips
4. **Flexible**: Custom llm_node override allows full control
5. **Integrated**: LiveKit handles STT/TTS/session management
6. **No Extra Costs**: Minimal API calls (no thread creation overhead)

### Current Limitations
1. **No Persistent Memory**: Conversation context lost after session
2. **No File Storage**: Can't attach files to assistant
3. **No Vector Search**: Can't use knowledge base retrieval
4. **Context Size Limit**: All context must fit in prompt
5. **No Session Recovery**: Can't resume interrupted conversation

---

## 11. Comparison Table

| Feature | Current (LiveKit) | OpenAI Assistants |
|---------|-------------------|-------------------|
| **Framework** | LiveKit Agents 1.0 | OpenAI Beta API |
| **LLM Calls** | Direct (per-message) | Via Threads |
| **Memory** | Local buffer only | Persistent (API) |
| **Tools** | Python functions | JSON schemas |
| **Context Injection** | llm_node() override | Message in thread |
| **File Support** | No | Yes (Vector store) |
| **Code Execution** | No | Yes (beta) |
| **Session Resumption** | No | Yes (thread_id) |
| **Latency** | Very low | Slightly higher (polling) |
| **Cost** | Low | Medium (extra API calls) |
| **Implementation** | ~500 lines | ~800+ lines |

---

## 12. Recommendations

### If Staying with Current System:
1. Add proper thread-like conversation tracking (UUID per call)
2. Implement smarter context windowing for long conversations
3. Consider caching visual context updates
4. Add conversation export feature (markdown/PDF)

### If Switching to Assistants API:
1. Create new branch: `feature/assistants-api`
2. Implement `AssistantAwareAgent` (copy VisualAwareAgent as template)
3. Create Assistants configuration and initialization
4. Build tool executor for Assistants-style tool calls
5. Test conversation persistence and memory
6. Benchmark latency impact (polling vs direct calls)
7. Plan gradual migration (feature flag?)

### Hybrid Approach (Recommended):
1. Keep LiveKit for STT/TTS/session management (excellent)
2. Switch LLM backend to Assistants API for conversation memory
3. Keep visual context injection pattern (but via messages)
4. Keep Python function tools (wrap in executor)
5. Get best of both: LiveKit speed + Assistants memory

---

## Files Analyzed

### Core Agent Files
- `/var/www/avatar/avatary/agent.py` (685 lines) - Main entrypoint
- `/var/www/avatar/avatary/prompts.py` (195 lines) - Instructions
- `/var/www/avatar/avatary/visual_aware_agent.py` (113 lines) - Custom agent
- `/var/www/avatar/avatary/visual_context_models.py` (99 lines) - Pydantic models

### Tool & Knowledge Base
- `/var/www/avatar/avatary/local_mcp_server.py` (200+ lines) - Tool definitions
- `/var/www/avatar/avatary/vision_processor.py` (200+ lines) - Vision integration

### Persistence & Call Center
- `/var/www/avatar/avatary/professional_conversation_manager.py` - Supabase persistence
- `/var/www/avatar/callCenter/openai_personas.py` (310 lines) - Personas
- `/var/www/avatar/callCenter/call_center_agent.py` (100+ lines) - Call center variant

### Configuration & Models
- `/var/www/avatar/avatary/models.py` (100+ lines) - Pydantic models
- `/var/www/avatar/avatary/requirements.txt` - Dependencies

---

## Next Steps for Migration Planning

1. **Decision Point**: Keep current or switch to Assistants API?
2. **If switching**: Create detailed migration spec with:
   - Thread creation/management strategy
   - Tool executor implementation
   - File upload strategy
   - Conversation recovery mechanism
3. **Testing**: Benchmarking latency and cost implications
4. **Rollout**: Feature flag for gradual migration

