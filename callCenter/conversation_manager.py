#!/usr/bin/env python3
"""
Conversation Manager for Call Center
Handles real-time conversations with OpenAI, persona switching, and transcription
"""

import logging
import os
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

# OpenAI imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Conversations will use mock responses.")

# Handle both relative and absolute imports
try:
    from .openai_personas import (
        get_persona_manager,
        PersonaType,
        RECEPTION_PERSONA,
        SALES_PERSONA,
        COMPLAINTS_PERSONA,
    )
    from .models import CallTranscript, TranscriptMessage
except ImportError:
    from openai_personas import (
        get_persona_manager,
        PersonaType,
        RECEPTION_PERSONA,
        SALES_PERSONA,
        COMPLAINTS_PERSONA,
    )
    from models import CallTranscript, TranscriptMessage


# ============================================================================
# CONVERSATION MESSAGE
# ============================================================================

class ConversationMessage:
    """Represents a single message in the conversation"""

    def __init__(self, role: str, content: str, persona: Optional[str] = None, timestamp: Optional[datetime] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.persona = persona  # which persona responded
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "persona": self.persona,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API format"""
        return {
            "role": self.role,
            "content": self.content,
        }


# ============================================================================
# CONVERSATION MANAGER
# ============================================================================

class ConversationManager:
    """Manages multi-turn conversations with persona switching"""

    def __init__(self, call_id: str, customer_name: str = "Customer", language: str = "en"):
        self.call_id = call_id
        self.customer_name = customer_name
        self.language = language
        self.messages: List[ConversationMessage] = []
        self.persona_manager = get_persona_manager()
        self.current_persona = PersonaType.RECEPTION
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                logger.info(f"OpenAI client initialized for call {call_id}")
            else:
                logger.warning("OPENAI_API_KEY not found. Using mock responses.")

        # Add initial greeting
        self._add_initial_greeting()

    def _add_initial_greeting(self):
        """Add initial greeting from reception"""
        greeting_en = f"Hello {self.customer_name}! Welcome to Ornina. I'm Ahmed from our reception team. How can I help you today?"
        greeting_ar = f"مرحبا {self.customer_name}! أهلا وسهلا في أورنينا. أنا أحمد من فريق الاستقبال. كيف يمكنني مساعدتك اليوم؟"

        greeting = greeting_ar if self.language.lower() in ["ar", "arabic"] else greeting_en
        self.add_assistant_message(greeting, PersonaType.RECEPTION)

    def add_user_message(self, content: str):
        """Add a user message to the conversation"""
        message = ConversationMessage("user", content)
        self.messages.append(message)
        self.conversation_history.append(message.to_openai_format())
        logger.debug(f"Added user message to call {self.call_id}: {content[:100]}")

    def add_assistant_message(self, content: str, persona: PersonaType):
        """Add an assistant message to the conversation"""
        message = ConversationMessage("assistant", content, persona=persona.value)
        self.messages.append(message)
        self.conversation_history.append(message.to_openai_format())
        logger.debug(f"Added assistant message ({persona.value}) to call {self.call_id}: {content[:100]}")

    async def get_response(self, user_message: str, force_persona: Optional[PersonaType] = None) -> str:
        """
        Get OpenAI response for user message
        Optionally force a specific persona, or auto-detect from context
        """
        # Add user message to history
        self.add_user_message(user_message)

        # Determine which persona should respond
        persona = force_persona or await self._detect_persona(user_message)
        self.current_persona = persona

        # Get system prompt for the persona
        system_prompt = self.persona_manager.get_system_prompt(persona, self.language)

        # Get response from OpenAI or use mock
        if self.openai_client:
            response = await self._get_openai_response(system_prompt, user_message)
        else:
            response = await self._get_mock_response(persona, user_message)

        # Add response to conversation history
        self.add_assistant_message(response, persona)

        return response

    async def _get_openai_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I apologize, but I'm having trouble processing your request. Please try again."

    async def _get_openai_response_stream(self, system_prompt: str, user_message: str) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=500,
                stream=True,
            )

            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Add full response to history after streaming completes
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield "I apologize, but I'm having trouble processing your request. Please try again."

    async def _detect_persona(self, user_message: str) -> PersonaType:
        """
        Detect which persona should respond based on user message
        Uses keywords and context to determine routing
        """
        message_lower = user_message.lower()

        # Check for complaint keywords
        complaint_keywords = ["problem", "issue", "complaint", "broken", "error", "wrong", "bad",
                            "مشكلة", "شكوى", "خطأ", "عطل", "سيء", "لا يعمل"]
        if any(keyword in message_lower for keyword in complaint_keywords):
            return PersonaType.COMPLAINTS

        # Check for sales/service interest keywords
        sales_keywords = ["price", "cost", "quote", "offer", "interested", "buy", "purchase", "service",
                         "سعر", "تكلفة", "عرض", "مهتم", "شراء", "خدمة"]
        if any(keyword in message_lower for keyword in sales_keywords):
            return PersonaType.SALES

        # Check for information requests
        info_keywords = ["information", "info", "about", "tell me", "what is", "how",
                        "معلومات", "عن", "ما هو", "كيف"]
        if any(keyword in message_lower for keyword in info_keywords):
            return PersonaType.RECEPTION

        # Default to current persona if not a clear switch
        return self.current_persona

    async def _get_mock_response(self, persona: PersonaType, user_message: str) -> str:
        """
        Generate a mock response for testing when OpenAI is not available
        """
        persona_info = self.persona_manager.get_persona_info(persona)

        if persona == PersonaType.RECEPTION:
            responses = [
                f"Thank you for that information, {self.customer_name}. Let me help you with that.",
                "I understand. Let me provide you with more details about our services.",
                "That's great! We have several options that might interest you.",
            ]
        elif persona == PersonaType.SALES:
            responses = [
                "Excellent! That's one of our most popular services. Let me tell you more about it.",
                "I'm excited to share how we can help with that. We have a proven track record.",
                "Great choice! Our team specializes in that area. Would you like to see some examples?",
            ]
        elif persona == PersonaType.COMPLAINTS:
            responses = [
                "I'm very sorry to hear that. I want to help resolve this for you. Can you tell me more details?",
                "I understand your concern, and I appreciate you bringing this to our attention.",
                "Let me get this documented right away so we can find the best solution.",
            ]
        else:
            responses = ["How can I assist you further?"]

        # Use the first response for now (in production, use more sophisticated routing)
        return responses[0]

    def switch_persona(self, new_persona: PersonaType):
        """Manually switch to a different persona"""
        self.current_persona = new_persona
        self.persona_manager.set_current_persona(new_persona)
        logger.info(f"Switched persona to {new_persona.value} for call {self.call_id}")

    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get the current conversation transcript"""
        return [msg.to_dict() for msg in self.messages]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history in OpenAI format"""
        return self.conversation_history.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "call_id": self.call_id,
            "customer_name": self.customer_name,
            "language": self.language,
            "current_persona": self.current_persona.value,
            "total_messages": len(self.messages),
            "user_messages": len([m for m in self.messages if m.role == "user"]),
            "assistant_messages": len([m for m in self.messages if m.role == "assistant"]),
            "personas_used": list(set([m.persona for m in self.messages if m.persona])),
            "started_at": self.messages[0].timestamp.isoformat() if self.messages else None,
            "last_message_at": self.messages[-1].timestamp.isoformat() if self.messages else None,
        }

    def to_call_transcript(self) -> CallTranscript:
        """Convert conversation to CallTranscript model"""
        messages = []
        for msg in self.messages:
            # Map role to speaker (customer, agent, bot, system)
            speaker_map = {
                "user": "customer",
                "assistant": "agent",
                "system": "system"
            }
            speaker = speaker_map.get(msg.role, "agent")

            transcript_msg = TranscriptMessage(
                speaker=speaker,
                content=msg.content,
                timestamp=msg.timestamp,
                language=self.language,
            )
            messages.append(transcript_msg)

        return CallTranscript(
            call_id=self.call_id,
            customer_name=self.customer_name,
            messages=messages,
            keywords=list(set([p for p in self.persona_manager.personas.keys() if p]))
        )


# ============================================================================
# SINGLETON MANAGER (PER CALL)
# ============================================================================

_conversation_managers: Dict[str, ConversationManager] = {}


def get_conversation_manager(call_id: str, customer_name: str = "Customer", language: str = "en") -> ConversationManager:
    """Get or create a conversation manager for a specific call"""
    if call_id not in _conversation_managers:
        _conversation_managers[call_id] = ConversationManager(call_id, customer_name, language)
    return _conversation_managers[call_id]


def remove_conversation_manager(call_id: str):
    """Remove conversation manager when call ends"""
    if call_id in _conversation_managers:
        del _conversation_managers[call_id]


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "ConversationMessage",
    "ConversationManager",
    "get_conversation_manager",
    "remove_conversation_manager",
]
