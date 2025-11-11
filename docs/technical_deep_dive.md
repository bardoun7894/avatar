# Technical Deep Dive - Agent Implementation Details

## Overview
This document provides code-level details on how the current agent system works, with specific line references and code snippets.

---

## 1. Agent Initialization Flow

### Step 1: Entry Point (`agent.py`, lines 103-111)

```python
async def entrypoint(ctx: agents.JobContext):
    import sys
    sys.stderr.write("\n" + "="*60 + "\n")
    sys.stderr.write("اتصال جديد! - NEW CONNECTION ENTRYPOINT CALLED!\n")
    sys.stderr.write("="*60 + "\n\n")
```

**What Happens**:
- LiveKit calls this function when a new connection is made
- `ctx` is a `JobContext` containing room, participant info
- Console output for debugging

### Step 2: Configuration Loading (`agent.py`, lines 117-237)

```python
# Line 118: Avatar mode (audio vs video)
avatar_provider = os.environ.get("AVATAR_PROVIDER", "audio").lower()

# Line 129-132: Load MCP tools
local_tools = get_local_tools()
print(f"\nتحميل {len(local_tools)} أداة محلية - Loading {len(local_tools)} local tools...")

# Line 202: Create LLM
session_config["llm"] = openai.LLM(model="gpt-4o-mini")

# Line 206-209: Create TTS
session_config["tts"] = openai.TTS(
    voice="alloy",
    speed=1.0
)

# Line 233: Create STT
session_config["stt"] = openai.STT(language="ar")

# Line 234: Create VAD
session_config["vad"] = silero.VAD.load()
```

**Dependencies at this stage**:
- `livekit.plugins.openai` (LLM, TTS, STT)
- `livekit.plugins.silero` (VAD)
- `prompts.AGENT_INSTRUCTIONS` (system prompt)

### Step 3: Visual Context Initialization (`agent.py`, lines 243-254)

```python
# Line 244-247: Create Pydantic-based visual store
visual_store = VisualContextStore(
    enabled=True,
    max_age_seconds=15.0
)

# Line 251-254: Create custom agent with visual awareness
agent = VisualAwareAgent(
    instructions=AGENT_INSTRUCTIONS,
    visual_store=visual_store
)
```

**Key Point**: The agent is instantiated with:
- Full instructions (from `prompts.py`)
- Visual context store (Pydantic model)

### Step 4: Tool Registration (`agent.py`, lines 258-322)

This is the most complex part - tools are registered by:

1. **Getting tool definitions** (line 267-270):
   ```python
   local_tools = get_local_tools()  # Returns list of dicts
   for tool in local_tools:
       tool_name = tool["name"]
       tool_desc = tool["description"]
       tool_schema = tool["inputSchema"]  # JSON schema
   ```

2. **Building function signature from schema** (lines 272-293):
   ```python
   type_map = {
       "string": str, "integer": int, "number": float,
       "boolean": bool, "array": list, "object": dict,
   }
   
   for p_name, p_details in schema_props.items():
       json_type = p_details.get("type", "string")
       py_type = type_map.get(json_type, str)
       annotations[p_name] = py_type
   ```

3. **Creating async tool function** (lines 296-309):
   ```python
   def make_tool_fn(name, desc, sig_params, annots):
       async def tool_fn(**kwargs):
           result = call_tool(name, kwargs)  # Calls local_mcp_server.call_tool()
           return json.dumps(result)
       
       tool_fn.__signature__ = inspect.Signature(parameters=sig_params)
       tool_fn.__name__ = name
       tool_fn.__doc__ = desc
       tool_fn.__annotations__ = {'return': str, **annots}
       return tool_fn
   ```

4. **Decorating with LiveKit's function_tool()** (lines 313-314):
   ```python
   decorated_func = function_tool()(func)
   tools.append(decorated_func)
   ```

5. **Registering on agent** (lines 318-320):
   ```python
   if hasattr(agent, '_tools') and isinstance(agent._tools, list):
       agent._tools.extend(tools)
   ```

### Step 5: Session Start (`agent.py`, lines 461-467)

```python
await session.start(
    room=ctx.room,
    agent=agent,
    room_input_options=RoomInputOptions(
        noise_cancellation=noise_cancellation.BVC(),
    ),
)
```

At this point:
- Agent is ready to receive user input
- STT listens for audio
- LLM is ready to process messages
- Tools are registered and ready to call

---

## 2. Message Flow & Context Injection

### Message Event System (`agent.py`, lines 391-415)

LiveKit fires events automatically:

```python
@session.on("conversation_item_added")
def on_conversation_item_added(event: ConversationItemAddedEvent):
    """Called by LiveKit when any message is added"""
    role = event.item.role  # "user" or "assistant"
    content = event.item.text_content
    
    if content and content.strip():
        # 1. Save immediately
        save_message(role=role, content=content)
        
        # 2. Add to professional manager buffer
        prof_manager.add_message_to_local_transcript(
            role=role,
            content=content,
            metadata={"language": "ar"}
        )
```

**When this fires**:
- After STT completes (user message)
- After LLM response is generated (assistant message)
- NOT fired for system messages or tool calls

### Context Injection Flow (`visual_aware_agent.py`, lines 35-71)

This is the critical override:

```python
async def llm_node(
    self,
    chat_ctx: llm.ChatContext,  # Contains message history
    tools: list[llm.FunctionTool],  # Tools available
    model_settings: Any,  # LLM settings
) -> AsyncIterable[llm.ChatChunk]:
    """Called by LiveKit before EVERY LLM call"""
    
    # Step 1: Get fresh visual context
    current_visual = self.visual_store.get_current()
    
    if current_visual:
        # Step 2: Check if fresh (less than 15 seconds old)
        if current_visual.age_seconds > self.visual_store.max_age_seconds:
            current_visual = None
    
    if current_visual:
        # Step 3: Create injection text
        visual_message = current_visual.to_injection_text()
        
        # Step 4: Add to chat context BEFORE LLM call
        chat_ctx.add_message(
            role="system",
            content=visual_message
        )
        
        logger.info(f"💉 Injecting visual context ({current_visual.age_seconds:.1f}s old)")
    
    # Step 5: Delegate to default LLM processing
    async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
        yield chunk
```

**Why this works**:
- `llm_node()` is called ONCE per LLM generation
- Chat context is passed in with message history
- We can modify it before passing to default handler
- LiveKit handles the actual API call

### Visual Context Model (`visual_context_models.py`, lines 11-53)

```python
class VisualAnalysis(BaseModel):
    content: str  # The analysis text from GPT-4V
    timestamp: datetime  # When created
    confidence: Optional[str]  # low/medium/high
    
    @property
    def age_seconds(self) -> float:
        """Calculate freshness"""
        return (datetime.now() - self.timestamp).total_seconds()
    
    def to_injection_text(self) -> str:
        """Format for LLM injection"""
        return f"""
[SYSTEM - VISUAL CONTEXT]
وقت التحديث: {time_str}
أنت تستطيع رؤية المستخدم الآن من خلال الكاميرا!
YOU CAN NOW SEE THE USER THROUGH THE CAMERA!

ما تراه:
{self.content}

⚠️ مهم جداً: استخدم ما تراه في ردك!
VERY IMPORTANT: Use what you see in your response!
"""
```

**Key design**:
- Context data is stored in Pydantic model (type-safe)
- Timestamps are automatic
- Freshness checked before injection
- Formatted as system message with bilingual text

---

## 3. Vision Processing Loop

### Continuous Analysis (`vision_processor.py`, lines 130-160)

```python
async def start_continuous_analysis(
    self,
    video_track: rtc.RemoteVideoTrack,
    callback: Callable
):
    """Main vision loop - runs continuously"""
    self.is_running = True
    
    while self.is_running:
        current_time = time.time()
        
        # Only analyze every 3 seconds
        if current_time - self.last_frame_time > self.analysis_interval:
            # Capture frame
            frame_bytes = await self.capture_frame_from_track(video_track)
            
            if frame_bytes:
                # Analyze with GPT-4 Vision
                analysis = await self.analyze_image(frame_bytes)
                
                if analysis and callback:
                    # Call handler with analysis
                    await callback(analysis, frame_bytes)
                
                self.last_frame_time = current_time
        
        await asyncio.sleep(0.5)  # Check every 500ms
```

### Frame Capture (`vision_processor.py`, lines 27-70)

```python
async def capture_frame_from_track(
    self, 
    video_track: rtc.RemoteVideoTrack
) -> Optional[bytes]:
    """Get one frame and convert to JPEG"""
    stream = None
    try:
        # Create video stream
        stream = rtc.VideoStream(video_track)
        
        async for event in stream:
            frame = event.frame
            
            # Convert to RGBA
            argb_frame = frame.convert(rtc.VideoBufferType.RGBA)
            
            # Create PIL Image
            img = Image.frombytes(
                "RGBA",
                (frame.width, frame.height),
                argb_frame.data
            )
            
            # Convert to RGB and encode as JPEG
            rgb_img = img.convert("RGB")
            buffered = io.BytesIO()
            rgb_img.save(buffered, format="JPEG", quality=60)
            
            jpeg_bytes = buffered.getvalue()
            
            # Return first frame
            return jpeg_bytes
    finally:
        if stream:
            await stream.aclose()
```

### Vision Analysis (`vision_processor.py`, lines 72-125)

```python
async def analyze_image(self, image_bytes: bytes) -> Optional[str]:
    """Send to GPT-4 Vision API"""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Professional exhibition-focused prompt
    prompt = """أنت مساعد ذكي في معرض تقنيات الذكاء الاصطناعي...
    
Your task:
1. Identify the main subject/activity
2. Note interactive elements
3. Assess setting context
4. Provide brief observations (2-3 sentences max)
"""
    
    try:
        response = await self.client.vision.analyze(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        return None
```

### Callback Handler (`agent.py`, lines 489-601)

This is called when vision analysis is complete:

```python
async def handle_visual_update(analysis: str, frame_bytes: bytes = None):
    """Process visual analysis results"""
    nonlocal greeted_people, greeting_flags
    
    recognized_person = None
    
    # Try face recognition if enabled
    if FACE_RECOGNITION_ENABLED and frame_bytes:
        try:
            match = face_recognizer.recognize_person(frame_bytes)
            if match.matched:
                recognized_person = match.user_name
                print(f"👤 RECOGNIZED: {match.user_name}")
                
                # Greet once per session
                if match.phone not in greeted_people and \
                   not greeting_flags["initial_greeting_sent"]:
                    greeting_flags["initial_greeting_sent"] = True
                    greeted_people.add(match.phone)
                    
                    # Personalized greeting
                    greeting = f"مرحباً سيدي {match.user_name}..."
                    await session.say(greeting, allow_interruptions=True)
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
    
    # Update visual context for next LLM call
    if recognized_person:
        agent.update_visual_context(f"Current person: {recognized_person}")
    else:
        print(f"👤 No person recognized")
```

---

## 4. Tool Execution Flow

### Tool Call Path

```
User: "شو الخدمات يلي عندكم؟" (What services do you have?)
     ↓
LLM (with tools available):
     "I should search_knowledge_base"
     Generates function call: search_knowledge_base(query="خدمات الشركة")
     ↓
LiveKit intercepts function call
     ↓
Tool Decorator (@function_tool()) recognizes the call
     ↓
Calls decorated_func(query="خدمات الشركة")
     ↓
async def tool_fn(**kwargs):
     result = call_tool("search_knowledge_base", kwargs)
     return json.dumps(result)
     ↓
local_mcp_server.call_tool("search_knowledge_base", ...)
     ↓
kb_manager.smart_search("خدمات الشركة")
     ↓
Returns: {"success": True, "results": [...]}
     ↓
Formatted JSON returned to LLM
     ↓
LLM generates final response with tool data:
     "لدينا 6 خدمات رئيسية..."
     ↓
User hears response via TTS
```

### Knowledge Base Search (`local_mcp_server.py`, lines 62-100)

```python
def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if tool_name == "search_knowledge_base":
            query = arguments.get("query", "")
            
            # Call smart search
            results = kb_manager.smart_search(query)
            
            if results["total_results"] == 0:
                return {
                    "success": True,
                    "message": "لم أجد نتائج مباشرة",
                    "results": []
                }
            
            # Format results
            formatted_results = []
            
            for faq in results["faqs"]:
                formatted_results.append({
                    "type": "FAQ",
                    "question": faq["question"],
                    "answer": faq["answer"]
                })
            
            # Return formatted
            return {
                "success": True,
                "total_results": len(formatted_results),
                "results": formatted_results
            }
```

---

## 5. Conversation Persistence

### Event Listener (`agent.py`, lines 391-415)

```python
@session.on("conversation_item_added")
def on_conversation_item_added(event: ConversationItemAddedEvent):
    try:
        role = event.item.role
        content = event.item.text_content
        
        if content and content.strip():
            # 1. Save message immediately
            save_message(role=role, content=content)
            
            # 2. Add to buffer
            prof_manager.add_message_to_local_transcript(
                role=role,
                content=content,
                metadata={"language": "ar"}
            )
    except Exception as e:
        print(f"⚠️  Error logging message: {e}")
```

### Shutdown Callback (`agent.py`, lines 417-455)

```python
async def save_final_conversation():
    """Called when session ends"""
    try:
        print("\n🏁 Call ended - Saving to database...")
        
        # Save everything at once
        result = prof_manager.end_conversation(
            user_name=extracted_user_info.get("name"),
            user_phone=extracted_user_info.get("phone"),
            user_email=extracted_user_info.get("email"),
            summary=f"محادثة مع {extracted_user_info.get('name') or 'عميل'}"
        )
        
        if result:
            print(f"✅ Conversation saved successfully!")
            print(f"   Messages: {result['messages_saved']}")
            if result.get('duration_seconds'):
                print(f"   Duration: {result['duration_seconds']:.1f}s")
        
        # Save user if we have info
        if extracted_user_info.get("name") and extracted_user_info.get("phone"):
            users_manager.save_user(
                name=extracted_user_info["name"],
                phone=extracted_user_info["phone"],
                email=extracted_user_info.get("email")
            )
    except Exception as e:
        print(f"❌ Error saving conversation: {e}")

ctx.add_shutdown_callback(save_final_conversation)
```

### Professional Manager (`professional_conversation_manager.py`)

```python
class ProfessionalConversationManager:
    def __init__(self):
        self.current_conversation_id: Optional[str] = None
        self.local_transcript: List[Dict] = []  # Buffer in memory
        self.conversation_metadata: Dict = {}
    
    def start_conversation(self, conversation_id, room_name, ...):
        """Create conversation record"""
        self.current_conversation_id = conversation_id
        self.local_transcript = []
        
        # Insert into database
        response = self.supabase.table('conversations').insert({
            "conversation_id": conversation_id,
            "room_name": room_name,
            "started_at": datetime.now().isoformat(),
            "status": "active",
        }).execute()
        
        return response.data[0] if response.data else None
    
    def add_message_to_local_transcript(self, role, content, metadata):
        """Buffer message (fast, no DB call)"""
        self.local_transcript.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
    
    def end_conversation(self, user_name=None, user_phone=None, ...):
        """Save buffered messages to database"""
        # Insert all buffered messages at once
        for msg in self.local_transcript:
            self.supabase.table('conversation_messages').insert({
                "conversation_id": self.current_conversation_id,
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"],
            }).execute()
        
        return {"messages_saved": len(self.local_transcript), ...}
```

---

## 6. Current Agent Instructions

### Instruction Structure (`prompts.py`)

The system prompt is a single string `AGENT_INSTRUCTIONS` (195 lines):

1. **Company Info** (lines 8-18)
   - Address, phone, social media
   - Company mission & values

2. **Services** (lines 20-51)
   - 6 services described with details
   - 3-5 bullet points each

3. **Training Programs** (lines 52-83)
   - 6 training programs
   - Duration, content, outcomes

4. **Conversation Flow** (lines 84-125)
   - 7-step conversation guide
   - What to do in each step
   - Sample questions

5. **Tool Usage Guidelines** (lines 126-185)
   - CRITICAL: Use info from THIS file first
   - Only use database for prices, dates
   - Examples of when to use tools
   - Examples of when NOT to use tools

6. **Tips** (lines 186-195)
   - Keep user info
   - Use natural dialect
   - Explain benefits
   - Be enthusiastic

### Tool Usage Rules

```
RULE 1: 答1 و أخيراً: اجب دائماً من المعلومات الموجودة أعلاه في هذا الملف
        "ALWAYS answer from information IN THIS FILE"

RULE 2: لا تستخدم قاعدة البيانات أبداً لهذه الأسئلة
        "NEVER use database for these questions (services, training, contact)"

RULE 3: استخدم قاعدة البيانات فقط لأسئلة محددة جداً
        "Only use database for prices, dates, specific details"

Example:
- User: "شو مدة دورة التسويق؟"
- Agent: "45 ساعة" (from prompts.py, no tool call)

- User: "كم سعر دورة التسويق؟"
- Agent: "لحظة خليني شوف..." → call search_knowledge_base (tool call needed)
```

---

## 7. Call Center Personas System

### Persona Manager (`openai_personas.py`, lines 232-310)

```python
class OpenAIPersonaManager:
    def __init__(self):
        self.personas = {
            PersonaType.RECEPTION: RECEPTION_PERSONA,
            PersonaType.SALES: SALES_PERSONA,
            PersonaType.COMPLAINTS: COMPLAINTS_PERSONA,
        }
        self.current_persona: Optional[PersonaType] = PersonaType.RECEPTION
    
    def get_system_prompt(self, persona_type: PersonaType, language: str = "en"):
        """Get system prompt for given persona & language"""
        persona = self.personas.get(persona_type)
        if language.lower() in ["ar", "arabic"]:
            return persona.system_prompt_ar
        return persona.system_prompt_en
    
    def set_current_persona(self, persona_type: PersonaType):
        """Switch persona mid-call"""
        self.current_persona = persona_type
```

### Persona Definitions

Each persona is a `PersonaConfig` with:
- name (English)
- name_ar (Arabic)
- department
- tone (style)
- tone_ar (style in Arabic)
- system_prompt_en
- system_prompt_ar

**Example: RECEPTION_PERSONA**
```python
RECEPTION_PERSONA = PersonaConfig(
    name="Ahmed",
    name_ar="أحمد",
    department="Reception",
    tone="Friendly, helpful, professional",
    system_prompt_en="""You are Ahmed, a friendly reception agent...
Your role:
- Greet customers warmly
- Collect their basic information
- Provide company information
- Listen to understand their needs
- Prepare to route to appropriate department
...
""",
    system_prompt_ar="""أنت أحمد، موظف استقبال ودود واحترافي...
دورك:
- الترحيب بالعملاء بدفء
- جمع معلوماتهم الأساسية
...
""",
)
```

---

## 8. Key Data Models

### VisualContextStore (Pydantic)

```python
class VisualContextStore(BaseModel):
    latest_analysis: Optional[VisualAnalysis] = Field(
        default=None,
        description="Most recent visual analysis"
    )
    enabled: bool = Field(
        default=True,
        description="Whether visual context injection is enabled"
    )
    max_age_seconds: float = Field(
        default=15.0,
        description="Maximum age for context to be considered valid"
    )
    
    def get_current(self) -> Optional[VisualAnalysis]:
        """Get current analysis if fresh enough"""
        if not self.enabled or not self.latest_analysis:
            return None
        
        if self.latest_analysis.age_seconds > self.max_age_seconds:
            return None  # Too old
        
        return self.latest_analysis
```

### User Models (from models.py)

```python
class User(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    email: Optional[EmailStr] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_interaction: datetime = Field(default_factory=datetime.now)
```

---

## 9. Configuration & Environment

### Required Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase (for persistence)
SUPABASE_URL=https://...supabase.co
SUPABASE_ANON_KEY=eyJ...

# LiveKit
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Optional: Avatar
AVATAR_PROVIDER=audio  # or "tavus"
TAVUS_API_KEY=...
TAVUS_PERSONA_ID=...
TAVUS_REPLICA_ID=...

# Optional: ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=G1QUjBCuRBbLbAmYlTgl
```

---

## 10. Performance Considerations

### Timing

- **Vision Analysis**: Every 3 seconds (configurable)
- **Visual Context Freshness**: 15 seconds (configurable)
- **VAD Response**: Real-time (Silero)
- **STT Latency**: Real-time (OpenAI)
- **LLM Latency**: 1-3 seconds (gpt-4o-mini)
- **TTS Latency**: Real-time streaming (OpenAI)

### Memory Usage

- **Visual Context Store**: ~1KB per update
- **Local Transcript Buffer**: ~100 bytes per message
- **Face Recognition DB**: ~100MB (InsightFace embeddings)
- **Per-Session Memory**: ~10MB (average conversation)

### API Call Counts

Per call:
- STT: 1 call per user message
- LLM: 1-2 calls per response (1 for response, +1 if tool call)
- TTS: 1 call per agent response
- Vision: 1 call per 3 seconds of video
- Database: 1 call per message (async, batched at end)

---

## 11. Error Handling & Logging

### Logging Strategy

```python
# Stderr for debug
sys.stderr.write("message")

# Print for info
print(f"✅ Success message")
print(f"⚠️  Warning message")
print(f"❌ Error message")

# Logging module for errors
import logging
logger = logging.getLogger(__name__)
logger.error(f"Error: {e}")
```

### Try-Except Pattern

Every async operation has try-except:

```python
try:
    result = await some_operation()
    print(f"✅ Success")
except Exception as e:
    print(f"⚠️  Error: {e}")
    import traceback
    traceback.print_exc()
    # Continue with fallback
```

---

## 12. Integration Points

### LiveKit Integration
- `agents.cli.run_app()` - Start agent
- `agents.JobContext` - Connection context
- `AgentSession` - Session management
- `ConversationItemAddedEvent` - Message events
- `rtc.RemoteVideoTrack` - Video input

### OpenAI Integration
- `livekit.plugins.openai.LLM()` - Chat completions
- `livekit.plugins.openai.TTS()` - Text to speech
- `livekit.plugins.openai.STT()` - Speech to text
- `AsyncOpenAI()` - Vision analysis

### Database Integration
- Supabase Python client
- Tables: conversations, conversation_messages, users
- Operations: insert, batch insert, select

---

## Summary

The system is well-designed with:
- Clean separation of concerns
- Proper async/await patterns
- Type-safe Pydantic models
- Good error handling
- Efficient context management
- Professional persistence layer

The main missing piece for Assistants API integration is:
- No persistent thread management (created fresh each call)
- No thread_id tracking (context lost after session)
- No Assistant creation/configuration
- No run-based execution model

