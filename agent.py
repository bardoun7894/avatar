from dotenv import load_dotenv
import asyncio
import os
import unittest.mock

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RoomOutputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
    tavus
)

from mcp_client import MCPServerSse
from mcp_client.agent_tools import MCPToolsIntegration

from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTIONS)


async def entrypoint(ctx: agents.JobContext):
    # Check if we're in console mode by checking if ctx.room is a mock
    is_console_mode = isinstance(ctx.room, unittest.mock.Mock)
    
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral"
        ),
    )

    # Initialize avatar with error handling (only in non-console mode)
    avatar = None
    if not is_console_mode:
        try:
            avatar = tavus.AvatarSession(
                replica_id=os.environ.get("REPLICA_ID"),  # ID of Tavus replica to use
                persona_id=os.environ.get("PERSONA_ID"),  # ID of Tavus persona to use (see preceding section for configuration details)
                api_key=os.environ.get("TAVUS_API_KEY"),
            )
        except Exception as e:
            print(f"Error initializing Tavus avatar: {e}")
            print("Please check your TAVUS_API_KEY and ensure you have sufficient credits.")
            return
    
    # Start avatar with error handling (only in non-console mode)
    if not is_console_mode and avatar:
        try:
            await avatar.start(session, room=ctx.room)
        except Exception as e:
            print(f"Error starting avatar session: {e}")
            if "out of conversational credits" in str(e):
                print("Your Tavus account is out of credits. Please add more credits to continue.")
            return

    # Initialize MCP server with error handling
    try:
        mcp_server = MCPServerSse(
            params={"url": os.environ.get("ZAPIER_MCP_SERVER_URL")},
            cache_tools_list=True,
            name="SSE MCP Server"
        )
    except Exception as e:
        print(f"Error initializing MCP server: {e}")
        print("Please check your ZAPIER_MCP_SERVER_URL environment variable.")
        mcp_server = None

    # Create agent with or without MCP tools
    if mcp_server:
        try:
            agent = await MCPToolsIntegration.create_agent_with_tools(
                agent_class=Assistant,
                mcp_servers=[mcp_server]
            )
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            print("Continuing without MCP tools...")
            agent = Assistant()
    else:
        agent = Assistant()

    # Start session with proper console mode handling
    try:
        if is_console_mode:
            # Console mode - use text-only with transcription
            await session.start(
                room=ctx.room,
                agent=agent,
                room_input_options=RoomInputOptions(
                    audio=False,  # Disable audio input in console mode
                ),
                room_output_options=RoomOutputOptions(
                    audio=False,  # Disable audio output in console mode
                    transcription=True,  # Enable text output
                ),
            )
        else:
            # Normal mode - use audio
            await session.start(
                room=ctx.room,
                agent=agent,
                room_input_options=RoomInputOptions(
                    # LiveKit Cloud enhanced noise cancellation
                    # - If self-hosting, omit this parameter
                    # - For telephony applications, use `BVCTelephony` for best results
                    noise_cancellation=noise_cancellation.BVC(),
                ),
            )
    except Exception as e:
        print(f"Error starting session: {e}")
        # Try with minimal settings
        try:
            await session.start(
                room=ctx.room,
                agent=agent,
            )
        except Exception as e2:
            print(f"Failed to start session with minimal settings: {e2}")
            return
    
    # Add cleanup handler to ensure proper session termination
    try:
        print("\n✅ Session started successfully!")
        print("💡 To avoid losing credits:")
        print("  - Press [Q] to quit when done")
        print("  - Use Ctrl+C to terminate if needed")
        
        # Keep the session running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Session terminated by user")
    except Exception as e:
        print(f"\n⚠️ Session error: {e}")
    finally:
        # Clean up resources to prevent credit loss
        print("\n🧹 Cleaning up session...")
        try:
            if avatar:
                await avatar.stop()
                print("✅ Avatar session stopped")
        except Exception as e:
            print(f"⚠️ Error stopping avatar: {e}")
        
        try:
            if session:
                await session.close()
                print("✅ Session closed")
        except Exception as e:
            print(f"⚠️ Error closing session: {e}")
        
        print("✅ Cleanup complete - Credits should be preserved")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
