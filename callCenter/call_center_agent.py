#!/usr/bin/env python3
"""
Call Center LiveKit Agent
Automated agent for handling call center interactions with real-time STT/LLM/TTS
Uses the official LiveKit AgentSession pattern
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, ChatMessage
from livekit.plugins import openai, silero

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Call Center Prompts
CALL_CENTER_SYSTEM_PROMPT = """
أنت مساعد استقبال آلي احترافي في مركز الاتصالات. You are a professional automated receptionist for a call center.

Your responsibilities:
- Welcome customers professionally in both Arabic and English
- Understand their needs and concerns
- Route them to appropriate departments (reception, sales, complaints)
- Maintain a friendly and helpful tone
- Be concise and clear in your responses
- Speak in complete sentences and be natural

Important:
1. Listen carefully to understand the customer's needs
2. Be empathetic and professional
3. Provide clear information about available services
4. Never put customers on hold without explanation
5. Transfer appropriately when needed

Respond in both Arabic and English to be inclusive.
"""

WELCOME_MESSAGE = "أهلاً وسهلاً بكم في خدمة الاستقبال الآلية. Welcome to our automated reception service. How can we help you today?"


async def entrypoint(ctx: AgentSession):
    """
    Main agent entrypoint - called when agent joins a room
    Uses official LiveKit AgentSession pattern with LLM, STT, TTS

    Args:
        ctx: The AgentSession context with room information, STT, LLM, TTS pre-configured
    """
    logger.info(f"📞 Agent joining room: {ctx.room.name}")
    logger.info(f"👥 Participants: {len(ctx.room.participants)}")

    # Log STT, LLM, TTS availability
    logger.info(f"🎤 STT available: {ctx.stt is not None}")
    logger.info(f"🧠 LLM available: {ctx.llm is not None}")
    logger.info(f"🔊 TTS available: {ctx.tts is not None}")

    # Initialize conversation with system prompt
    ctx.chat_history.add_messages(
        ChatMessage(
            role="system",
            content=CALL_CENTER_SYSTEM_PROMPT,
        ),
    )

    # Send welcome message using TTS
    logger.info("🎙️ Sending welcome message...")
    try:
        # Use ctx.say() to speak with TTS
        await ctx.say(WELCOME_MESSAGE, allow_interruptions=True)
        logger.info("✅ Welcome message sent")
    except Exception as e:
        logger.error(f"❌ Error sending welcome message: {e}")
        import traceback
        traceback.print_exc()

    # Main conversation loop
    logger.info("🔄 Starting conversation loop...")
    try:
        while ctx.room.is_connected:
            # Wait for user speech using STT
            logger.debug("⏳ Waiting for user input...")

            # Listen for user input
            try:
                user_input = await ctx.asr.recognize()  # Use ASR (Automatic Speech Recognition)

                if user_input and user_input.strip():
                    logger.info(f"👤 User: {user_input}")

                    # Add user message to chat history
                    ctx.chat_history.add_user_message(user_input)

                    # Get LLM response
                    logger.debug("🧠 Generating LLM response...")
                    response = await ctx.llm.chat(chat_history=ctx.chat_history)

                    if response and response.message:
                        assistant_message = response.message.content
                        logger.info(f"🤖 Agent: {assistant_message}")

                        # Add assistant response to chat history
                        ctx.chat_history.add_assistant_message(assistant_message)

                        # Speak the response using TTS
                        logger.debug("🔊 Speaking response...")
                        await ctx.say(assistant_message, allow_interruptions=True)
                    else:
                        logger.warning("⚠️  Empty response from LLM")
                else:
                    logger.debug("No user input detected, continuing...")

            except asyncio.TimeoutError:
                logger.debug("⏱️  Timeout waiting for user input")
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                logger.info("🛑 Conversation cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in conversation loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"❌ Fatal error in agent: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("👋 Agent session ending")


async def on_session_shutdown(ctx: AgentSession):
    """Handle agent shutdown"""
    logger.info(f"🔌 Agent disconnecting from room: {ctx.room.name}")


def main():
    """Main entry point - creates and runs the LiveKit agent worker"""
    logger.info("🚀 Call Center Agent starting...")
    logger.info(f"📡 LiveKit URL: {LIVEKIT_URL}")
    logger.info(f"✅ OpenAI API Key set: {bool(OPENAI_API_KEY)}")

    # Create agent worker
    agent_worker = agents.Worker(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
        name="call-center-agent",
    )

    # Configure agent with LLM, STT, TTS (will be added to ctx in entrypoint)
    # This uses the environment variables OPENAI_API_KEY by default

    # Register entrypoint and shutdown handlers
    agent_worker.on_agent_start(entrypoint)
    agent_worker.on_agent_shutdown(on_session_shutdown)

    logger.info("✅ Call Center Agent initialized")
    logger.info("🎧 Listening for incoming calls...")

    # Run the worker - this blocks until shutdown
    agent_worker.run()


if __name__ == "__main__":
    main()
