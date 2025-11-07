from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
    silero,
)

# Import ElevenLabs for Arabic voice
try:
    from livekit.plugins import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

import os
import logging
import re
from prompts import AGENT_INSTRUCTIONS
from local_mcp_server import get_local_tools, call_tool
from conversation_logger import ConversationLogger
from users_manager import UsersManager

load_dotenv()

# Initialize conversation logger and users manager
conversation_logger = ConversationLogger()
users_manager = UsersManager()

# Helper function to extract user info from text
def extract_user_info(text: str):
    """Extract name and phone from Arabic/English text"""
    info = {"name": None, "phone": None}

    # Phone patterns (various formats)
    phone_patterns = [
        r'\+?\d{10,15}',  # International format
        r'\d{4,5}\s?\d{2}\s?\d{2}',  # Local format with spaces
        r'\d{7,}',  # Simple digit sequence
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            info["phone"] = match.group(0).strip()
            break

    # Name patterns - look for Arabic names or "اسمي" patterns
    name_patterns = [
        r'اسمي\s+([أ-ي\s]+)',  # "My name is ..."
        r'أنا\s+([أ-ي\s]+)',    # "I am ..."
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # English names
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            info["name"] = match.group(1).strip()
            break

    return info

logger = logging.getLogger(__name__)

# Global storage for conversation
conversation_context = {
    'agent': None,
    'conversation_id': None,
    'last_user_msg': None,
    'last_assistant_msg': None
}

async def entrypoint(ctx: agents.JobContext):
    print("\n" + "="*60)
    print("اتصال جديد! - NEW CONNECTION!")
    print("="*60 + "\n")

    # Avatar mode configuration
    avatar_provider = os.environ.get("AVATAR_PROVIDER", "audio").lower()
    print(f"Avatar Mode: {avatar_provider.upper()}")

    # Voice configuration
    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
    elevenlabs_voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "G1QUjBCuRBbLbAmYlTgl")

    print(f"اللغة: العربية - Language: Arabic")
    print(f"الصوت: أبو سالم (ذكر كويتي) - Voice: Abu Salem")
    print(f"Voice ID: {elevenlabs_voice_id}")

    # Get local tools
    local_tools = get_local_tools()
    print(f"\nتحميل {len(local_tools)} أداة محلية - Loading {len(local_tools)} local tools...")
    for tool in local_tools:
        print(f"   {tool['name']}: {tool['description'][:50]}...")

    # Create conversation ID
    conversation_id = ctx.room.name or f"session-{os.urandom(4).hex()}"
    print(f"\nConversation ID: {conversation_id}")
    conversation_context['conversation_id'] = conversation_id

    # Helper to save message
    def save_message(role: str, content: str):
        """Save message to database"""
        if not content or not content.strip():
            return

        print(f"\n[{role.upper()}]: {content[:100]}...")

        try:
            conversation_logger.save_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                room_name=ctx.room.name,
                metadata={"language": "ar"}
            )
            print(f"تم حفظ رسالة - {role} message saved!")

            # Extract user info if user message
            if role == "user":
                user_info = extract_user_info(content)
                if user_info["name"] and user_info["phone"]:
                    print(f"اكتشاف معلومات المستخدم: {user_info['name']} - {user_info['phone']}")
                    try:
                        users_manager.save_user(
                            name=user_info["name"],
                            phone=user_info["phone"]
                        )
                        print("تم حفظ المستخدم - User saved!")
                    except Exception as e:
                        print(f"خطأ في حفظ المستخدم: {e}")

        except Exception as e:
            print(f"خطأ في حفظ الرسالة: {e}")
            import traceback
            traceback.print_exc()

    # Create session configuration
    session_config = {}

    # Use OpenAI LLM
    session_config["llm"] = openai.LLM(model="gpt-4o-mini")

    # Configure ElevenLabs TTS
    if ELEVENLABS_AVAILABLE and elevenlabs_api_key:
        try:
            print("\nتكوين صوت أبو سالم...")
            tts = elevenlabs.TTS(
                model="eleven_turbo_v2_5",
                voice_id=elevenlabs_voice_id,
                api_key=elevenlabs_api_key,
                language="ar",
            )
            session_config["tts"] = tts
            print("تم تكوين الصوت الذكري بنجاح - Male voice configured!")
        except Exception as e:
            print(f"فشل ElevenLabs: {e}")
            print("استخدام صوت OpenAI البديل...")
            session_config["tts"] = openai.TTS(voice="onyx")
    else:
        print("ElevenLabs not available, using OpenAI voice (onyx)")
        session_config["tts"] = openai.TTS(voice="onyx")

    # Arabic STT with VAD
    session_config["stt"] = openai.STT(language="ar")
    session_config["vad"] = silero.VAD.load()
    print("التعرف على الكلام العربي جاهز - Arabic STT ready")
    print("VAD (Voice Activity Detection) مفعل - VAD enabled")

    session = AgentSession(**session_config)

    # Create agent
    agent = Agent(instructions=AGENT_INSTRUCTIONS)
    print("تم إنشاء الوكيل - Agent created")

    # Register tools with the agent
    print("\nتسجيل الأدوات مع الوكيل - Registering tools...")

    from livekit.agents.llm import function_tool
    import json
    import inspect

    # Create decorated tool functions
    tools = []
    for tool in local_tools:
        tool_name = tool["name"]
        tool_desc = tool["description"]
        tool_schema = tool["inputSchema"]

        # Build function parameters from schema
        params = []
        annotations = {}
        schema_props = tool_schema.get("properties", {})
        schema_required = set(tool_schema.get("required", []))
        type_map = {
            "string": str, "integer": int, "number": float,
            "boolean": bool, "array": list, "object": dict,
        }

        for p_name, p_details in schema_props.items():
            json_type = p_details.get("type", "string")
            py_type = type_map.get(json_type, str)
            annotations[p_name] = py_type

            default = inspect.Parameter.empty if p_name in schema_required else None
            params.append(inspect.Parameter(
                name=p_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=py_type,
                default=default
            ))

        # Create the tool function with closure
        def make_tool_fn(name, desc, sig_params, annots):
            async def tool_fn(**kwargs):
                print(f"\nاستدعاء أداة: {name} - Calling tool")
                print(f"   Parameters: {kwargs}")
                result = call_tool(name, kwargs)
                print(f"   Result: {result.get('success', False)}")
                return json.dumps(result)

            tool_fn.__signature__ = inspect.Signature(parameters=sig_params)
            tool_fn.__name__ = name
            tool_fn.__doc__ = desc
            tool_fn.__annotations__ = {'return': str, **annots}

            return tool_fn

        # Create and decorate the function
        func = make_tool_fn(tool_name, tool_desc, params, annotations)
        decorated_func = function_tool()(func)
        tools.append(decorated_func)
        print(f"   {tool_name}")

    # Add tools to agent
    if hasattr(agent, '_tools') and isinstance(agent._tools, list):
        agent._tools.extend(tools)
        print(f"تم تسجيل {len(tools)} أداة - Registered {len(tools)} tools!")
    else:
        print("تحذير: الوكيل لا يحتوي على _tools")

    print(f"\nحفظ المحادثات مفعّل - Conversation logging ENABLED")

    # Initialize Tavus video avatar AFTER session creation
    avatar_session = None
    if avatar_provider == "tavus":
        try:
            from livekit.plugins import tavus
            print("\nتهيئة Tavus Video Avatar - Initializing Tavus...")
            print(f"   Persona ID: {os.environ.get('TAVUS_PERSONA_ID', 'NOT SET')}")
            print(f"   Replica ID: {os.environ.get('TAVUS_REPLICA_ID', 'NOT SET')}")

            avatar_session = tavus.AvatarSession(
                api_key=os.environ.get("TAVUS_API_KEY"),
                persona_id=os.environ.get("TAVUS_PERSONA_ID"),
                replica_id=os.environ.get("TAVUS_REPLICA_ID"),
            )
            print("تم إنشاء Tavus session - Tavus session created")
        except Exception as e:
            print(f"فشل Tavus: {e}")
            import traceback
            traceback.print_exc()
            print("الاستمرار بدون فيديو - Continuing in audio-only mode...")
            avatar_provider = "audio"
            avatar_session = None

    # Start session
    try:
        print("\nالاتصال بالغرفة - Connecting to room...")

        # Start Tavus avatar first if enabled
        if avatar_session:
            print("بدء Tavus video avatar - Starting Tavus video avatar...")
            await avatar_session.start(session, ctx.room)
            print("Tavus avatar started successfully!")
            print("الفيديو يجب أن يظهر الآن - Video should appear now!")
        else:
            print("Agent in audio-only mode...")

        # SIMPLE APPROACH: Wrap the LLM's chat method
        original_chat = session._llm.chat if hasattr(session, '_llm') else None

        if original_chat:
            async def logged_chat(*, chat_ctx, fnc_ctx=None, **kwargs):
                """Wrap chat to capture messages"""
                # Log user messages before calling LLM
                if hasattr(chat_ctx, 'messages'):
                    for msg in chat_ctx.messages:
                        if hasattr(msg, 'role') and msg.role == 'user':
                            content = None
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, str):
                                    content = msg.content
                                elif isinstance(msg.content, list):
                                    for c in msg.content:
                                        if hasattr(c, 'text'):
                                            content = c.text
                                            break

                            if content and content != conversation_context['last_user_msg']:
                                save_message("user", content)
                                conversation_context['last_user_msg'] = content

                # Call original
                result = await original_chat(chat_ctx=chat_ctx, fnc_ctx=fnc_ctx, **kwargs)

                # Log assistant response after LLM responds
                async for chunk in result:
                    # Check for assistant message in chunk
                    if hasattr(chunk, 'choices'):
                        for choice in chunk.choices:
                            if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                                content = choice.delta.content
                                if content:
                                    # Accumulate response
                                    if not conversation_context['last_assistant_msg']:
                                        conversation_context['last_assistant_msg'] = ""
                                    conversation_context['last_assistant_msg'] += content

                    yield chunk

                # Save complete response
                if conversation_context['last_assistant_msg']:
                    save_message("assistant", conversation_context['last_assistant_msg'])
                    conversation_context['last_assistant_msg'] = None

            session._llm.chat = logged_chat
            print("✅ Wrapped LLM chat method")

        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )

        print("\n" + "="*60)
        print("الوكيل جاهز! - AGENT READY!")
        print("="*60)
        print("الاستماع للغة العربية - Listening for Arabic...")
        print("يتحدث: أبو سالم (صوت ذكري) - Speaking: Abu Salem")
        print("قل: السلام عليكم - Say: Assalamu Alaikum")
        print("="*60 + "\n")

    except Exception as e:
        print(f"فشل بدء الجلسة - Failed to start: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
