#!/usr/bin/env python3
"""
Audio Orchestrator for Call Center
Connects speech-to-text, LLM, and text-to-speech in real-time conversation loop
"""

import os
import logging
import asyncio
import json
from typing import Optional, Callable, List, Dict
from datetime import datetime
from dotenv import load_dotenv

# Audio components
from audio_handler import AudioHandler
from openai_personas import PersonaManager
from call_router import CallRouter
from crm_system import CRMSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")


class AudioOrchestrator:
    """
    Orchestrates real-time audio conversation flow:
    Audio Input → STT → LLM → TTS → Audio Output
    """

    def __init__(self):
        """Initialize the audio orchestrator with all components"""
        logger.info("🎼 Initializing Audio Orchestrator...")

        # Audio processing
        self.audio_handler = AudioHandler()

        # AI personas and routing
        self.persona_manager = PersonaManager()
        self.call_router = CallRouter()

        # Customer context
        self.crm_system = CRMSystem()

        # Conversation state per call
        self.active_conversations: Dict[str, dict] = {}

        logger.info("✅ Audio Orchestrator initialized")

    async def start_conversation(
        self,
        call_id: str,
        customer_phone: str,
        initial_persona: str = "reception",
        on_transcript_update: Optional[Callable] = None,
        on_audio_ready: Optional[Callable] = None
    ) -> bool:
        """
        Start a new conversation orchestration

        Args:
            call_id: Unique call identifier
            customer_phone: Customer's phone number
            initial_persona: Starting persona ('reception', 'sales', or 'support')
            on_transcript_update: Callback when transcript updates
            on_audio_ready: Callback when audio response is ready

        Returns:
            True if conversation started successfully
        """
        try:
            logger.info(f"🎙️  Starting conversation - Call: {call_id}, Customer: {customer_phone}")

            # Initialize conversation state
            self.active_conversations[call_id] = {
                "call_id": call_id,
                "customer_phone": customer_phone,
                "current_persona": initial_persona,
                "conversation_history": [],
                "sentiment_history": [],
                "started_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "callbacks": {
                    "transcript": on_transcript_update,
                    "audio_ready": on_audio_ready
                }
            }

            # Load customer context
            customer_context = await self._load_customer_context(customer_phone)

            # Initialize conversation history with system prompt
            persona = self.persona_manager.get_persona(initial_persona)
            system_prompt = await self._build_system_prompt(persona, customer_context)

            self.active_conversations[call_id]["conversation_history"] = [
                {"role": "system", "content": system_prompt}
            ]

            logger.info(f"✅ Conversation initialized for {call_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start conversation: {e}")
            return False

    async def process_audio_chunk(
        self,
        call_id: str,
        audio_bytes: bytes,
        audio_format: str = "webm"
    ) -> bool:
        """
        Process incoming audio chunk from customer

        Flow: Audio → STT → Sentiment → Routing → LLM → TTS → Callback

        Args:
            call_id: Call identifier
            audio_bytes: Audio data
            audio_format: Audio format (webm, wav, mp3, etc.)

        Returns:
            True if processing successful
        """
        if call_id not in self.active_conversations:
            logger.error(f"Call {call_id} not found in active conversations")
            return False

        try:
            conversation = self.active_conversations[call_id]
            logger.debug(f"🔄 Processing audio chunk for call {call_id}")

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 1: Speech-to-Text (STT)
            # ═══════════════════════════════════════════════════════════════════════
            logger.info("🎤 Transcribing audio...")
            transcription_result = self.audio_handler.transcribe_audio(audio_bytes)

            if not transcription_result.get("success"):
                logger.error(f"❌ Transcription failed: {transcription_result.get('error')}")
                return False

            user_text = transcription_result.get("text", "").strip()
            language = transcription_result.get("language", DEFAULT_LANGUAGE)
            confidence = transcription_result.get("confidence", 0)

            if not user_text:
                logger.debug("⏭️  No speech detected, skipping turn")
                return True

            logger.info(f"👤 User: {user_text} (confidence: {confidence:.1%})")

            # Notify transcript callback
            if conversation["callbacks"]["transcript"]:
                await self._call_callback(
                    conversation["callbacks"]["transcript"],
                    {
                        "type": "user_transcript",
                        "text": user_text,
                        "language": language,
                        "confidence": confidence
                    }
                )

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 2: Sentiment Analysis & Routing Decision
            # ═══════════════════════════════════════════════════════════════════════
            logger.info("📊 Analyzing sentiment for routing...")
            sentiment = await self._analyze_sentiment(user_text, language)

            # Record sentiment
            conversation["sentiment_history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "text": user_text,
                "sentiment": sentiment
            })

            # Determine if routing is needed
            current_persona = conversation["current_persona"]
            recommended_persona = self.call_router.route_by_sentiment(
                sentiment=sentiment,
                current_persona=current_persona
            )

            if recommended_persona != current_persona:
                logger.info(f"🔄 Routing from {current_persona} → {recommended_persona}")
                conversation["current_persona"] = recommended_persona

                # Notify about handoff
                if conversation["callbacks"]["transcript"]:
                    await self._call_callback(
                        conversation["callbacks"]["transcript"],
                        {
                            "type": "persona_switch",
                            "from": current_persona,
                            "to": recommended_persona,
                            "reason": sentiment
                        }
                    )

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 3: Add to Conversation History
            # ═══════════════════════════════════════════════════════════════════════
            conversation["conversation_history"].append({
                "role": "user",
                "content": user_text,
                "metadata": {
                    "language": language,
                    "confidence": confidence,
                    "sentiment": sentiment
                }
            })

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 4: Get LLM Response
            # ═══════════════════════════════════════════════════════════════════════
            logger.info(f"🧠 Getting LLM response from {conversation['current_persona']}...")
            persona = self.persona_manager.get_persona(conversation["current_persona"])

            llm_response = await self._get_llm_response(
                messages=conversation["conversation_history"],
                persona=persona,
                customer_context=conversation.get("customer_context", {})
            )

            if not llm_response:
                logger.error("❌ LLM failed to generate response")
                fallback_response = self._get_fallback_response(conversation["current_persona"])
                llm_response = fallback_response

            assistant_text = llm_response.strip()
            logger.info(f"🤖 Agent: {assistant_text}")

            # Add to conversation history
            conversation["conversation_history"].append({
                "role": "assistant",
                "content": assistant_text,
                "metadata": {
                    "persona": conversation["current_persona"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 5: Text-to-Speech (TTS)
            # ═══════════════════════════════════════════════════════════════════════
            logger.info("🔊 Synthesizing speech...")
            tts_result = self.audio_handler.synthesize_speech(
                text=assistant_text,
                language=language,
                persona=conversation["current_persona"]
            )

            if not tts_result:
                logger.error("❌ TTS synthesis failed")
                return False

            # Get audio file path
            audio_file = tts_result.get("file_path") or tts_result.get("filename")
            if not audio_file:
                logger.error("❌ No audio file returned from TTS")
                return False

            # Read audio file and prepare for transmission
            try:
                with open(audio_file, "rb") as f:
                    audio_data = f.read()
            except Exception as e:
                logger.error(f"❌ Failed to read audio file {audio_file}: {e}")
                return False

            logger.info(f"✅ Audio ready ({len(audio_data)} bytes)")

            # ═══════════════════════════════════════════════════════════════════════
            # STEP 6: Notify Audio Ready (send back to client)
            # ═══════════════════════════════════════════════════════════════════════
            if conversation["callbacks"]["audio_ready"]:
                await self._call_callback(
                    conversation["callbacks"]["audio_ready"],
                    {
                        "call_id": call_id,
                        "audio_bytes": audio_data,
                        "audio_format": "mp3",
                        "transcript": assistant_text,
                        "persona": conversation["current_persona"]
                    }
                )

            # Notify transcript with assistant's response
            if conversation["callbacks"]["transcript"]:
                await self._call_callback(
                    conversation["callbacks"]["transcript"],
                    {
                        "type": "assistant_transcript",
                        "text": assistant_text,
                        "persona": conversation["current_persona"],
                        "audio_ready": True
                    }
                )

            logger.info(f"✅ Audio processing complete for {call_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error processing audio chunk: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def end_conversation(self, call_id: str) -> Dict:
        """
        End a conversation and return summary

        Args:
            call_id: Call identifier

        Returns:
            Conversation summary
        """
        if call_id not in self.active_conversations:
            return {"error": f"Call {call_id} not found"}

        try:
            conversation = self.active_conversations[call_id]
            conversation["is_active"] = False
            conversation["ended_at"] = datetime.utcnow().isoformat()

            summary = {
                "call_id": call_id,
                "customer_phone": conversation["customer_phone"],
                "duration_seconds": (
                    datetime.fromisoformat(conversation["ended_at"]) -
                    datetime.fromisoformat(conversation["started_at"])
                ).total_seconds(),
                "personas_used": list(set(
                    msg.get("metadata", {}).get("persona", "unknown")
                    for msg in conversation["conversation_history"]
                    if msg.get("role") == "assistant"
                )),
                "sentiment_summary": {
                    "initial": conversation["sentiment_history"][0] if conversation["sentiment_history"] else None,
                    "final": conversation["sentiment_history"][-1] if conversation["sentiment_history"] else None,
                    "trend": self._analyze_sentiment_trend(conversation["sentiment_history"])
                },
                "message_count": len([m for m in conversation["conversation_history"] if m.get("role") in ["user", "assistant"]])
            }

            logger.info(f"✅ Conversation ended: {call_id}")
            return summary

        except Exception as e:
            logger.error(f"❌ Error ending conversation: {e}")
            return {"error": str(e)}

    # ═════════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═════════════════════════════════════════════════════════════════════════════

    async def _load_customer_context(self, phone: str) -> Dict:
        """Load customer information from CRM"""
        try:
            customer = self.crm_system.get_customer_by_phone(phone)
            if customer:
                return {
                    "name": customer.get("name"),
                    "phone": phone,
                    "tier": customer.get("tier"),
                    "vip": customer.get("vip", False),
                    "history": customer.get("history", [])
                }
            return {}
        except Exception as e:
            logger.warning(f"Could not load customer context: {e}")
            return {}

    async def _build_system_prompt(self, persona: Dict, customer_context: Dict) -> str:
        """Build system prompt with persona and customer context"""
        prompt = persona.get("system_prompt", "You are a helpful assistant.")

        if customer_context.get("name"):
            prompt += f"\n\nCustomer Info:\n- Name: {customer_context['name']}"
            if customer_context.get("vip"):
                prompt += "\n- VIP Status: Yes - Treat with priority"
            if customer_context.get("tier"):
                prompt += f"\n- Tier: {customer_context['tier']}"

        return prompt

    async def _analyze_sentiment(self, text: str, language: str = "ar") -> str:
        """Analyze sentiment of text"""
        # Placeholder - integrate with OpenAI or sentiment library
        # For now, return neutral
        return "neutral"

    async def _get_llm_response(
        self,
        messages: List[Dict],
        persona: Dict,
        customer_context: Dict
    ) -> Optional[str]:
        """Get response from LLM"""
        try:
            import openai

            openai.api_key = OPENAI_API_KEY

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None

    def _get_fallback_response(self, persona_name: str) -> str:
        """Get fallback response when LLM fails"""
        fallbacks = {
            "reception": "معاف، حدث خطأ مؤقت. Sorry, we're experiencing a temporary issue. Please try again.",
            "sales": "شكراً لاهتمامك. Thank you for your interest. Let me assist you shortly.",
            "support": "نحن هنا للمساعدة. We're here to help. Please bear with us."
        }
        return fallbacks.get(persona_name, "معاف. Sorry.")

    async def _call_callback(self, callback: Callable, data: Dict) -> None:
        """Call a callback function, handling both sync and async"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Callback error: {e}")

    def _analyze_sentiment_trend(self, sentiment_history: List[Dict]) -> str:
        """Analyze sentiment trend over conversation"""
        if len(sentiment_history) < 2:
            return "insufficient_data"

        sentiments = [s.get("sentiment", "neutral") for s in sentiment_history]
        first = sentiments[0]
        last = sentiments[-1]

        if first == last:
            return "stable"
        elif last in ["positive", "satisfied"]:
            return "improving"
        elif last in ["negative", "complaining"]:
            return "degrading"

        return "mixed"


# Global orchestrator instance
_orchestrator = None


def get_audio_orchestrator() -> AudioOrchestrator:
    """Get or create the global audio orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AudioOrchestrator()
    return _orchestrator


__all__ = ["AudioOrchestrator", "get_audio_orchestrator"]
