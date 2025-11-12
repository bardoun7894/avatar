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
import time
from datetime import datetime
from prompts import AGENT_INSTRUCTIONS
from local_mcp_server import get_local_tools, call_tool
from conversation_logger import ConversationLogger
from users_manager import UsersManager
from professional_conversation_manager import ProfessionalConversationManager
from vision_processor import VisionProcessor

# Import new visual context system
from visual_context_models import VisualContextStore
from visual_aware_agent import VisualAwareAgent

# Import workflow analyzer for performance tracking
from workflow_analyzer import workflow_analyzer

# Import face recognition system (InsightFace) - will be loaded lazily
FACE_RECOGNITION_ENABLED = True
face_recognizer = None

try:
    # Just check if module exists - don't load it yet
    import importlib.util
    spec = importlib.util.find_spec("insightface")
    if spec is None:
        FACE_RECOGNITION_ENABLED = False
    else:
        print("✅ Face recognition available (will load when needed)")
except Exception as e:
    FACE_RECOGNITION_ENABLED = False
    print(f"⚠️  Face recognition disabled: {e}")

load_dotenv()

# Initialize managers
conversation_logger = ConversationLogger()  # For message-by-message logging
users_manager = UsersManager()
prof_manager = ProfessionalConversationManager()  # For buffered conversation logging

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
    # Start workflow tracking
    workflow_analyzer.start_step("Connection Initialization")

    import sys
    sys.stderr.write("\n" + "="*60 + "\n")
    sys.stderr.write("اتصال جديد! - NEW CONNECTION ENTRYPOINT CALLED!\n")
    sys.stderr.write("="*60 + "\n\n")
    sys.stderr.flush()

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
    print(f"الصوت: OpenAI Alloy (ذكر) - Voice: OpenAI Alloy (Male - supports Arabic)")

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

    # Helper to save message (important for immediate logging)
    def save_message(role: str, content: str):
        """Save message to database immediately (not buffered)"""
        if not content or not content.strip():
            return

        print(f"\n[{role.upper()}]: {content[:100]}...")

        try:
            # DISABLED: Using prof_manager instead to avoid duplicates
            # conversation_logger.save_message(
            #     conversation_id=conversation_id,
            #     role=role,
            #     content=content,
            #     room_name=ctx.room.name,
            #     metadata={"language": "ar"}
            # )
            # print(f"تم حفظ رسالة - {role} message saved!")
            pass  # Messages will be saved via prof_manager instead

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
                        extracted_user_info["name"] = user_info["name"]
                        extracted_user_info["phone"] = user_info["phone"]
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

    workflow_analyzer.complete_step()
    workflow_analyzer.start_step("Session & Agent Configuration")

    session = AgentSession(**session_config)

    # Create visual context store using Pydantic
    visual_store = VisualContextStore(
        enabled=True,
        max_age_seconds=15.0  # Context expires after 15 seconds
    )
    print("✅ Visual context store created (Pydantic-based)")

    # Create Visual-Aware Agent (injects context before each LLM call)
    agent = VisualAwareAgent(
        instructions=AGENT_INSTRUCTIONS,
        visual_store=visual_store
    )
    print("تم إنشاء الوكيل - Visual-Aware Agent created")
    print("   Uses llm_node override for automatic context injection")

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
    tavus_log_file = "/tmp/tavus_init.log"

    if avatar_provider == "tavus":
        try:
            with open(tavus_log_file, "a") as f:
                f.write(f"\n=== Tavus Init Attempt at {os.environ.get('AVATAR_PROVIDER')} ===\n")
                f.write(f"API Key: {bool(os.environ.get('TAVUS_API_KEY'))}\n")
                f.write(f"Persona ID: {os.environ.get('TAVUS_PERSONA_ID')}\n")
                f.write(f"Replica ID: {os.environ.get('TAVUS_REPLICA_ID')}\n")
                f.flush()

            from livekit.plugins import tavus
            print("\nتهيئة Tavus Video Avatar - Initializing Tavus...")
            print(f"   API Key Set: {bool(os.environ.get('TAVUS_API_KEY'))}")
            print(f"   Persona ID: {os.environ.get('TAVUS_PERSONA_ID', 'NOT SET')}")
            print(f"   Replica ID: {os.environ.get('TAVUS_REPLICA_ID', 'NOT SET')}")

            api_key = os.environ.get("TAVUS_API_KEY")
            persona_id = os.environ.get("TAVUS_PERSONA_ID")
            replica_id = os.environ.get("TAVUS_REPLICA_ID")

            if not api_key or not persona_id or not replica_id:
                raise ValueError(f"Missing Tavus credentials: API_KEY={bool(api_key)}, PERSONA={bool(persona_id)}, REPLICA={bool(replica_id)}")

            with open(tavus_log_file, "a") as f:
                f.write("Creating TavusAvatarSession...\n")
                f.flush()

            avatar_session = tavus.AvatarSession(
                api_key=api_key,
                persona_id=persona_id,
                replica_id=replica_id,
            )
            print("✅ تم إنشاء Tavus session - Tavus session created successfully!")
            with open(tavus_log_file, "a") as f:
                f.write("✅ Tavus session created successfully!\n")
                f.flush()
        except Exception as e:
            print(f"❌ فشل Tavus: {e}")
            with open(tavus_log_file, "a") as f:
                f.write(f"❌ TAVUS ERROR: {e}\n")
                import traceback
                f.write(traceback.format_exc())
                f.flush()
            import traceback
            traceback.print_exc()
            print("⚠️  الاستمرار بدون فيديو - Continuing in audio-only mode...")
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
            """Log messages using both immediate and buffered logging"""
            try:
                role = event.item.role  # "user" or "assistant"
                content = event.item.text_content

                if content and content.strip():
                    # 1. Immediate logging to database (conversation_logger)
                    save_message(role=role, content=content)

                    # 2. Buffer locally for batch save at end (prof_manager)
                    prof_manager.add_message_to_local_transcript(
                        role=role,
                        content=content,
                        metadata={"language": "ar"}
                    )

            except Exception as e:
                print(f"⚠️  Error logging message: {e}")
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

        workflow_analyzer.complete_step()
        workflow_analyzer.start_step("Starting Avatar Session")

        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )

        workflow_analyzer.complete_step()

        print("\n" + "="*60)
        print("الوكيل الذكر جاهز! - MALE AGENT READY!")
        print("="*60)
        print("الاستماع للغة العربية - Listening for Arabic...")
        print("يتحدث: OpenAI Alloy (ذكر) - Speaking: OpenAI Alloy (Male)")
        print("قل: السلام عليكم - Say: Assalamu Alaikum")
        print("="*60 + "\n")

        # Initialize vision processor
        vision_processor = VisionProcessor()
        vision_task = None
        greeted_people = set()  # Track who we've already greeted in this session
        greeting_flags = {
            "initial_greeting_sent": True,  # ONE greeting per entire session
            "greeting_lock": False,
            "first_visual_time": datetime.now(),  # Track when first visual update arrived
            "session_identity": ctx.room.name or f"session-{os.urandom(4).hex()}"  # Unique session ID
        }

        async def handle_visual_update(analysis: str, frame_bytes: bytes = None):
            """
            Handle visual analysis updates with face recognition
            Greets recognized ministers by name FIRST, or uses general greeting if not recognized
            Only sends ONE greeting per session
            """
            nonlocal greeted_people, greeting_flags

            # Try face recognition if enabled and frame provided
            recognized_person = None
            if FACE_RECOGNITION_ENABLED and frame_bytes:
                try:
                    # Lazy load face recognizer on first use
                    global face_recognizer
                    if face_recognizer is None:
                        from insightface_recognition import face_recognizer as fr
                        face_recognizer = fr

                    workflow_analyzer.start_step("Face Recognition")
                    match = face_recognizer.recognize_person(frame_bytes)
                    workflow_analyzer.complete_step(matched=match.matched if match else False)
                    if match.matched:
                        recognized_person = match.user_name
                        print(f"👤 RECOGNIZED: {match.user_name} (confidence: {match.confidence:.0%})")

                        # ✅ SINGLE GREETING PER SESSION - Only greet once at the beginning
                        if not greeting_flags["initial_greeting_sent"]:
                            greeting_flags["initial_greeting_sent"] = True
                            greeted_people.add(match.phone)

                            # Build simple, natural Arabic greeting based on recognition
                            # Format: السلام عليكم [with title if VIP, just name if regular]
                            user_type = "guest"
                            user_context = ""

                            # Check for specific VIPs - use formal titles
                            if "Abd Salam Haykal" in match.user_name or "عبد السلام هيكل" in match.user_name:
                                user_type = "minister"
                                greeting = "السلام عليكم سيدي الوزير عبد السلام هيكل، أهلاً وسهلاً بك في شركة أورنينا"
                                user_context = "Government Minister: Abd Salam Haykal"
                            elif "Asaad Chaibani" in match.user_name or "أسعد شيباني" in match.user_name:
                                user_type = "minister"
                                greeting = "السلام عليكم سيدي الوزير أسعد شيباني، أهلاً وسهلاً بك في شركة أورنينا"
                                user_context = "Government Minister: Asaad Chaibani"
                            elif "Mohamed Bardouni" in match.user_name or "محمد البردوني" in match.user_name:
                                user_type = "developer"
                                greeting = "السلام عليكم سيدي محمد، أهلاً وسهلاً بك في شركة أورنينا"
                                user_context = "Developer: Mohamed Bardouni"
                            elif "Radwan Nassar" in match.user_name or "رضوان نصار" in match.user_name:
                                user_type = "ceo"
                                greeting = "السلام عليكم السيد رضوان نصار، أهلاً وسهلاً بك في شركة أورنينا"
                                user_context = "CEO of Ornina Media: Radwan Nassar"
                            elif "طارق مارديني" in match.user_name or "Tarik Mardini" in match.user_name:
                                user_type = "operations_director"
                                greeting = "السلام عليكم السيد طارق مارديني، أهلاً وسهلاً بك في شركة أورنينا"
                                user_context = "Operations Director & Board Member: Tarik Mardini"
                            else:
                                # Regular recognized person - simple greeting with name
                                user_type = "recognized_guest"
                                greeting = f"السلام عليكم السيد {match.user_name}، أهلاً وسهلاً بك"
                                user_context = f"Recognized Guest: {match.user_name}"

                            print(f"🎤 First Greeting ({user_type}): {greeting}")
                            print(f"   👥 {user_context}")
                            print(f"   ✅ Session: {greeting_flags['session_identity']} - NO MORE GREETINGS THIS SESSION")

                            workflow_analyzer.start_step("Deliver First Greeting")
                            await session.say(greeting, allow_interruptions=True)
                            workflow_analyzer.complete_step(person=match.user_name, user_type=user_type)

                            # Print performance report after first greeting
                            workflow_analyzer.print_report()

                        # Add recognition to context
                        recognition_text = f"\n\n👤 Person: {match.user_name}"
                        analysis = recognition_text
                    else:
                        # Not recognized yet - wait a few seconds before sending general greeting
                        # This gives face recognition multiple attempts to match
                        if not greeting_flags["initial_greeting_sent"]:
                            # Record first visual update time
                            if greeting_flags["first_visual_time"] is None:
                                greeting_flags["first_visual_time"] = time.time()
                                print(f"⏳ First visual update received. Waiting for face recognition...")

                            # Wait at least 3 seconds before sending general greeting
                            elapsed = time.time() - greeting_flags["first_visual_time"]
                            if elapsed > 3:
                                # Still not recognized after 3 seconds, send general greeting
                                greeting_flags["initial_greeting_sent"] = True
                                general_greeting = "السلام عليكم! أهلاً بك في شركة أورنينا للذكاء الاصطناعي. كيف بقدر ساعدك اليوم؟"
                                print(f"🎤 Sending general greeting (person not recognized after {elapsed:.1f}s)")
                                workflow_analyzer.start_step("Deliver First Greeting")
                                await session.say(general_greeting, allow_interruptions=True)
                                workflow_analyzer.complete_step(person="Unknown")

                                # Print performance report after first greeting
                                workflow_analyzer.print_report()
                            else:
                                print(f"   ⏳ Still waiting for recognition... {3-elapsed:.1f}s remaining")

                except Exception as e:
                    print(f"⚠️  Face recognition error: {e}")
                    # If error and no greeting sent yet, send general greeting ONLY ONCE
                    if not greeting_flags["initial_greeting_sent"]:
                        greeting_flags["initial_greeting_sent"] = True
                        general_greeting = "السلام عليكم! أهلاً بك في شركة أورنينا للذكاء الاصطناعي. كيف بقدر ساعدك اليوم؟"
                        print(f"🎤 Sending general greeting (recognition error)")
                        await session.say(general_greeting, allow_interruptions=True)

            # Update visual context in Pydantic store
            if recognized_person:
                agent.update_visual_context(f"Current person: {recognized_person}")
                print(f"✅ Visual context updated: {recognized_person}")
            else:
                # No one recognized
                print(f"👤 No person recognized")

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

                                workflow_analyzer.start_step("Vision Processing Startup")

                                # Start continuous vision analysis
                                try:
                                    vision_task = asyncio.create_task(
                                        vision_processor.start_continuous_analysis(
                                            video_track,
                                            callback=handle_visual_update
                                        )
                                    )
                                    workflow_analyzer.complete_step()
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
