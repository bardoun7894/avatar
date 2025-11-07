"""
Visual-Aware Agent
Custom Agent that injects visual context before each LLM call
Uses LiveKit Agents 1.0 llm_node pattern
"""

from livekit.agents import Agent, llm
from typing import AsyncIterable, Any
import logging
from visual_context_models import VisualContextStore

logger = logging.getLogger(__name__)


class VisualAwareAgent(Agent):
    """
    Custom Agent that injects visual context into chat before LLM processing

    This overrides llm_node to inject visual analysis as a system message
    before each LLM call, ensuring the avatar always has fresh visual context.
    """

    def __init__(self, instructions: str, visual_store: VisualContextStore):
        """
        Initialize Visual-Aware Agent

        Args:
            instructions: Base agent instructions
            visual_store: Pydantic store containing visual context
        """
        super().__init__(instructions=instructions)
        self.visual_store = visual_store
        self._base_instructions = instructions

    async def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: list[llm.FunctionTool],
        model_settings: Any,
    ) -> AsyncIterable[llm.ChatChunk]:
        """
        Override llm_node to inject visual context before LLM call

        This is the modern LiveKit Agents 1.0 way to inject context.
        Called before every LLM generation, ensuring fresh context.
        """

        # Get current visual analysis
        current_visual = self.visual_store.get_current()

        if current_visual:
            # Inject visual context as system message
            visual_message = current_visual.to_injection_text()

            logger.info(f"💉 Injecting visual context ({current_visual.age_seconds:.1f}s old)")
            logger.debug(f"   Content: {current_visual.content[:100]}...")

            # Add to chat context as system message
            # This appears BEFORE the user's message, giving the LLM context
            chat_ctx.add_message(
                role="system",
                content=visual_message
            )

            print(f"✅ Visual context injected into chat (age: {current_visual.age_seconds:.1f}s)")
        else:
            logger.debug("ℹ️  No fresh visual context available for injection")

        # Delegate to default LLM processing
        async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
            yield chunk

    def update_visual_context(self, analysis: str, confidence: str = None):
        """
        Update visual context (called by vision processor)

        Args:
            analysis: Visual analysis text from GPT-4 Vision
            confidence: Optional confidence level
        """
        visual_analysis = self.visual_store.update(analysis, confidence)

        logger.info(f"📸 Visual context updated")
        logger.debug(f"   Length: {len(analysis)} chars")
        logger.debug(f"   Time: {visual_analysis.timestamp.strftime('%H:%M:%S')}")

        print(f"👁️  Visual context updated: {analysis[:80]}...")

        return visual_analysis

    def clear_visual_context(self):
        """Clear visual context"""
        self.visual_store.clear()
        logger.info("🧹 Visual context cleared")

    def get_visual_status(self) -> dict:
        """Get current visual context status"""
        current = self.visual_store.get_current()

        if current:
            return {
                "has_context": True,
                "age_seconds": current.age_seconds,
                "is_fresh": current.is_fresh,
                "content_length": len(current.content),
                "timestamp": current.timestamp.isoformat()
            }
        else:
            return {
                "has_context": False,
                "reason": "no_data" if not self.visual_store.latest_analysis else "too_old"
            }
