from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ConversationItemAddedEvent
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
import asyncio
from prompts import AGENT_INSTRUCTIONS
from local_mcp_server import get_local_tools, call_tool
from conversation_logger import ConversationLogger
from users_manager import UsersManager
from professional_conversation_manager import ProfessionalConversationManager
from vision_processor import VisionProcessor

load_dotenv()

# Initialize managers
conversation_logger = ConversationLogger()  # Keep for backward compatibility
users_manager = UsersManager()
prof_manager = ProfessionalConversationManager()  # Professional system

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
    print(f"الصوت: OpenAI Alloy - Voice: OpenAI Alloy (supports Arabic)")

    # Get local tools
    local_tools = get_local_tools()
    print(f"\nتحميل {len(local_tools)} أداة محلية - Loading {len(local_tools)} local tools...")
    for tool in local_tools:
        print(f"   {tool['name']}: {tool['description'][:50]}...")

    # Create conversation ID
    conversation_id = ctx.room.name or f"session-{os.urandom(4).hex()}"
    print(f"\nConversation ID: {conversation_id}")
    conversation_context['conversation_id'] = conversation_id

    # Start professional conversation (creates record in database)
    try:
        participant_identity = None
        if hasattr(ctx, 'participant') and ctx.participant:
            participant_identity = ctx.participant.identity

        prof_manager.start_conversation(
            conversation_id=conversation_id,
            room_name=ctx.room.name,
            participant_identity=participant_identity,
            metadata={"language": "ar", "source": "voice_call"}
        )
    except Exception as e:
        print(f"⚠️  Could not start conversation record: {e}")

    # Track extracted user info globally
    extracted_user_info = {"name": None, "phone": None, "email": None}

    # Helper to save message (legacy - kept for compatibility)
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

    # Use OpenAI TTS (reliable and supports Arabic)
    print("\nاستخدام OpenAI TTS للصوت...")
    session_config["tts"] = openai.TTS(
        voice="alloy",  # Supports Arabic well
        speed=1.0
    )
    print("✅ تم تكوين OpenAI TTS - OpenAI TTS configured!")

    # Commented out ElevenLabs (having connection issues)
    # if ELEVENLABS_AVAILABLE and elevenlabs_api_key:
    #     try:
    #         print("\nتكوين صوت أبو سالم...")
    #         tts = elevenlabs.TTS(
    #             model="eleven_turbo_v2_5",
    #             voice_id=elevenlabs_voice_id,
    #             api_key=elevenlabs_api_key,
    #             language="ar",
    #         )
    #         session_config["tts"] = tts
    #         print("تم تكوين الصوت الذكري بنجاح - Male voice configured!")
    #     except Exception as e:
    #         print(f"فشل ElevenLabs: {e}")
    #         print("استخدام صوت OpenAI البديل...")
    #         session_config["tts"] = openai.TTS(voice="alloy")
    # else:
    #     print("ElevenLabs not available, using OpenAI voice (alloy)")
    #     session_config["tts"] = openai.TTS(voice="alloy")

    # Arabic STT with VAD
    session_config["stt"] = openai.STT(language="ar")
    session_config["vad"] = silero.VAD.load()
    print("التعرف على الكلام العربي جاهز - Arabic STT ready")
    print("VAD (Voice Activity Detection) مفعل - VAD enabled")

    session = AgentSession(**session_config)

    # Store visual context globally for injection
    vision_context = {"latest": None, "timestamp": None}

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

        # OFFICIAL LIVEKIT WAY: Listen to conversation_item_added event
        @session.on("conversation_item_added")
        def on_conversation_item_added(event: ConversationItemAddedEvent):
            """Buffer messages locally (fast, no database lag!)"""
            try:
                role = event.item.role  # "user" or "assistant"
                content = event.item.text_content

                if content and content.strip():
                    # Buffer locally (FAST - no database call!)
                    prof_manager.add_message_to_local_transcript(
                        role=role,
                        content=content,
                        metadata={"language": "ar"}
                    )

                    # Extract user info if user message
                    if role == "user":
                        user_info = extract_user_info(content)
                        if user_info["name"]:
                            extracted_user_info["name"] = user_info["name"]
                        if user_info["phone"]:
                            extracted_user_info["phone"] = user_info["phone"]

            except Exception as e:
                print(f"⚠️  Error buffering message: {e}")
                import traceback
                traceback.print_exc()

        print("✅ Listening to conversation_item_added event (local buffering)")

        # Add shutdown callback to save everything to database
        async def save_final_conversation():
            """Save complete conversation to database when call ends"""
            try:
                print("\n🏁 Call ended - Saving to database...")

                # Save everything to database
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

                    # Also save user to users table if we have info
                    if extracted_user_info.get("name") and extracted_user_info.get("phone"):
                        try:
                            users_manager.save_user(
                                name=extracted_user_info["name"],
                                phone=extracted_user_info["phone"],
                                email=extracted_user_info.get("email")
                            )
                            print(f"✅ User info saved: {extracted_user_info['name']}")
                        except Exception as e:
                            print(f"⚠️  Error saving user: {e}")

            except Exception as e:
                print(f"❌ Error saving conversation: {e}")
                import traceback
                traceback.print_exc()

        ctx.add_shutdown_callback(save_final_conversation)
        print("✅ Shutdown callback registered (professional system)")

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
        print("يتحدث: OpenAI Alloy - Speaking: OpenAI Alloy")
        print("قل: السلام عليكم - Say: Assalamu Alaikum")
        print("="*60 + "\n")

        # Initialize vision processor
        vision_processor = VisionProcessor()
        vision_task = None

        async def handle_visual_update(analysis: str):
            """Handle visual analysis updates - inject into agent instructions"""
            import time
            print(f"👁️  Visual analysis: {analysis[:100]}...")

            # Store context with timestamp
            vision_context["latest"] = analysis
            vision_context["timestamp"] = time.time()

            # Update agent instructions dynamically with visual context
            updated_instructions = (
                AGENT_INSTRUCTIONS +
                f"\n\n🎥 ما أراه الآن عبر الكاميرا (تحديث {time.strftime('%H:%M:%S')}):\n{analysis}"
            )

            # Use Pydantic-based Agent.update_instructions() method
            agent.update_instructions(updated_instructions)

            print(f"✅ Agent instructions updated with visual context via Pydantic model")

        # Monitor for video tracks
        async def monitor_video_tracks():
            """Monitor for user video tracks and start vision processing"""
            nonlocal vision_task

            print("👁️  Monitoring for video tracks...")
            print(f"    Local participant: {ctx.room.local_participant.identity}")

            # Wait for remote participants
            attempt = 0
            while True:
                await asyncio.sleep(2)
                attempt += 1

                # Get remote participants
                remote_participants = ctx.room.remote_participants

                # Log all participants every 5 attempts
                if attempt % 5 == 0:
                    print(f"👥 Remote participants in room ({len(remote_participants)}):")
                    for p in remote_participants.values():
                        print(f"   - {p.identity}: {len(p.track_publications)} tracks")

                for participant in remote_participants.values():
                    # Skip our own agent
                    if participant.identity == ctx.room.local_participant.identity:
                        continue

                    print(f"🔍 Checking participant: {participant.identity}")
                    print(f"   Tracks: {len(participant.track_publications)}")

                    # Look for video tracks
                    for track_sid, pub in participant.track_publications.items():
                        print(f"   Track {track_sid}: kind={pub.kind}, source={pub.source}, subscribed={pub.subscribed}")

                        # Check if it's a camera/video track
                        from livekit import rtc
                        if pub.source == rtc.TrackSource.SOURCE_CAMERA:
                            print(f"   ✅ Found camera track!")

                            # Subscribe if not already subscribed
                            if not pub.subscribed:
                                print(f"   📡 Subscribing to track...")
                                # Subscription happens automatically in LiveKit agents

                            # Wait a bit for subscription to complete
                            await asyncio.sleep(1)

                            if pub.track and not vision_task:
                                video_track = pub.track
                                print(f"📹 Got user video track from {participant.identity}")
                                print("🎥 Starting vision analysis...")

                                # Start continuous vision analysis
                                try:
                                    vision_task = asyncio.create_task(
                                        vision_processor.start_continuous_analysis(
                                            video_track,
                                            callback=handle_visual_update
                                        )
                                    )
                                    print("✅ Vision analysis task started!")
                                    return
                                except Exception as e:
                                    print(f"❌ Failed to start vision analysis: {e}")
                                    import traceback
                                    traceback.print_exc()

        # Start video monitoring in background
        asyncio.create_task(monitor_video_tracks())

    except Exception as e:
        print(f"فشل بدء الجلسة - Failed to start: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
