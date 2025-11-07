"""
Conversation Context Manager
Manages injection of visual context into conversation flow
"""

import time
from typing import Optional
from livekit.agents import llm, Agent, AgentSession
import logging

logger = logging.getLogger(__name__)


class ConversationContextManager:
    """Manages dynamic context injection into agent conversations"""

    def __init__(self, agent: Agent, session: AgentSession):
        self.agent = agent
        self.session = session
        self.visual_context: Optional[str] = None
        self.visual_timestamp: Optional[float] = None
        self.base_instructions: str = agent._instructions  # Store original

    def update_visual_context(self, analysis: str):
        """Update visual context and refresh agent instructions"""
        self.visual_context = analysis
        self.visual_timestamp = time.time()

        # Rebuild instructions with visual context
        updated_instructions = self._build_instructions()

        # Update agent using Pydantic method
        self.agent.update_instructions(updated_instructions)

        print(f"✅ Context Manager: Instructions updated with visual context")
        print(f"    Analysis length: {len(analysis)} chars")
        print(f"    Timestamp: {time.strftime('%H:%M:%S', time.localtime(self.visual_timestamp))}")

    def _build_instructions(self) -> str:
        """Build complete instructions with all context"""
        instructions = self.base_instructions

        # Add visual context if available and fresh (< 10 seconds old)
        if self.visual_context and self.visual_timestamp:
            age = time.time() - self.visual_timestamp
            if age < 10:
                visual_block = (
                    f"\n\n"
                    f"{'='*60}\n"
                    f"🎥 VISUAL CONTEXT - ما أراه الآن\n"
                    f"{'='*60}\n"
                    f"Updated: {time.strftime('%H:%M:%S', time.localtime(self.visual_timestamp))}\n"
                    f"\n{self.visual_context}\n"
                    f"{'='*60}\n"
                    f"⚠️ استخدم هذا السياق البصري في ردودك! Use this visual context in your responses!\n"
                    f"{'='*60}"
                )
                instructions += visual_block

        return instructions

    def get_visual_context(self) -> Optional[dict]:
        """Get current visual context with metadata"""
        if not self.visual_context:
            return None

        age = time.time() - self.visual_timestamp if self.visual_timestamp else None

        return {
            "content": self.visual_context,
            "timestamp": self.visual_timestamp,
            "age_seconds": age,
            "is_fresh": age < 10 if age is not None else False
        }

    async def inject_system_message(self, content: str):
        """
        Inject a system message into conversation
        (If supported by session - experimental)
        """
        try:
            # Try to use session say method
            await self.session.say(content, add_to_chat_ctx=True)
            print(f"✅ Context Manager: System message injected via session")
        except Exception as e:
            print(f"⚠️  Context Manager: Could not inject system message: {e}")

    def clear_visual_context(self):
        """Clear visual context and reset to base instructions"""
        self.visual_context = None
        self.visual_timestamp = None
        self.agent.update_instructions(self.base_instructions)
        print("🧹 Context Manager: Visual context cleared")