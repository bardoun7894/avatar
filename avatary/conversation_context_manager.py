"""
Conversation Context Manager (Updated for LiveKit Agents 1.0)

NOTE: This is now DEPRECATED in favor of VisualAwareAgent with llm_node override.
The new pattern injects context directly into chat before each LLM call,
which is more reliable than updating instructions.

Keep this for backward compatibility only.
"""

import time
from typing import Optional
from livekit.agents import llm, AgentSession
from visual_aware_agent import VisualAwareAgent
from visual_context_models import VisualContextStore
import logging

logger = logging.getLogger(__name__)


class ConversationContextManager:
    """
    Manages dynamic context injection into agent conversations

    DEPRECATED: Use VisualAwareAgent directly instead.
    This class is kept for backward compatibility.
    """

    def __init__(self, agent: VisualAwareAgent, session: AgentSession):
        """
        Initialize context manager

        Args:
            agent: VisualAwareAgent instance (must be VisualAwareAgent, not base Agent)
            session: AgentSession instance
        """
        self.agent = agent
        self.session = session

        logger.warning(
            "ConversationContextManager is deprecated. "
            "Use VisualAwareAgent.update_visual_context() directly."
        )

    def update_visual_context(self, analysis: str):
        """
        Update visual context (delegates to agent)

        DEPRECATED: Call agent.update_visual_context() directly instead
        """
        logger.warning("update_visual_context is deprecated. Use agent.update_visual_context()")
        return self.agent.update_visual_context(analysis)

    def get_visual_context(self) -> Optional[dict]:
        """
        Get current visual context with metadata

        DEPRECATED: Call agent.get_visual_status() directly instead
        """
        logger.warning("get_visual_context is deprecated. Use agent.get_visual_status()")
        return self.agent.get_visual_status()

    def clear_visual_context(self):
        """
        Clear visual context

        DEPRECATED: Call agent.clear_visual_context() directly instead
        """
        logger.warning("clear_visual_context is deprecated. Use agent.clear_visual_context()")
        self.agent.clear_visual_context()