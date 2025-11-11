#!/usr/bin/env python3
"""
Conversation Analyzer for Call Center
Uses Pydantic for validation and LangGraph-like state management for conversation flow
Analyzes intent, sentiment, and routes intelligently between personas
"""

import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS FOR CONVERSATION ANALYSIS
# ============================================================================

class ConversationIntent(str, Enum):
    """Detected intents in customer messages"""
    COMPLAINT = "complaint"
    SERVICE_INQUIRY = "service_inquiry"
    SALES_INTEREST = "sales_interest"
    TRAINING_INTEREST = "training_interest"
    BILLING_ISSUE = "billing_issue"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


class SentimentAnalysis(str, Enum):
    """Sentiment of customer message"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class PriorityLevel(str, Enum):
    """Priority level for routing"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class IntentAnalysis(BaseModel):
    """Pydantic model for intent analysis results"""
    intent: ConversationIntent
    confidence: float = Field(ge=0.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)
    language: str = Field(default="en", description="Detected language (en/ar)")
    reasoning: str = Field(description="Why this intent was detected")

    class Config:
        use_enum_values = True


class SentimentAnalysisResult(BaseModel):
    """Pydantic model for sentiment analysis"""
    sentiment: SentimentAnalysis
    confidence: float = Field(ge=0.0, le=1.0)
    emotion_indicators: List[str] = Field(default_factory=list)
    reasoning: str = Field(description="Why this sentiment was detected")

    class Config:
        use_enum_values = True


class RoutingDecision(BaseModel):
    """Pydantic model for routing decision"""
    target_persona: str = Field(description="Target persona (reception/sales/complaints)")
    priority: PriorityLevel
    suggested_action: str = Field(description="Suggested action for the agent")
    create_ticket: bool = Field(default=False, description="Whether to create a support ticket")
    escalation_needed: bool = Field(default=False, description="Whether escalation is needed")
    reasoning: str = Field(description="Reasoning for this decision")

    class Config:
        use_enum_values = True


class ConversationState(BaseModel):
    """Pydantic model for conversation state"""
    call_id: str
    customer_name: str
    language: str = Field(default="en")
    current_persona: str = Field(default="reception")
    message_count: int = Field(default=0, ge=0)
    user_message_count: int = Field(default=0, ge=0)
    conversation_duration_seconds: float = Field(default=0.0, ge=0.0)

    # Analysis results
    last_intent: Optional[ConversationIntent] = None
    last_sentiment: Optional[SentimentAnalysis] = None
    overall_sentiment: SentimentAnalysis = SentimentAnalysis.NEUTRAL

    # Engagement metrics
    customer_satisfaction: float = Field(default=0.5, ge=0.0, le=1.0)
    escalation_count: int = Field(default=0, ge=0)
    personas_used: List[str] = Field(default_factory=list)

    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ConversationIntent: lambda v: v.value if isinstance(v, ConversationIntent) else v,
            SentimentAnalysis: lambda v: v.value if isinstance(v, SentimentAnalysis) else v,
        }


class MessageAnalysis(BaseModel):
    """Pydantic model for individual message analysis"""
    call_id: str
    message: str
    role: str = Field(description="user or assistant")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Analysis results
    intent: IntentAnalysis
    sentiment: SentimentAnalysisResult
    routing_decision: Optional[RoutingDecision] = None

    # Content analysis
    requires_ticket: bool = Field(default=False)
    contact_info_provided: bool = Field(default=False)
    question_asked: bool = Field(default=False)
    complaint_indicated: bool = Field(default=False)


# ============================================================================
# CONVERSATION ANALYZER
# ============================================================================

class ConversationAnalyzer:
    """
    Analyzes conversations using Pydantic models
    Provides intent detection, sentiment analysis, and routing decisions
    """

    def __init__(self, call_id: str, customer_name: str = "Customer", language: str = "en"):
        self.state = ConversationState(
            call_id=call_id,
            customer_name=customer_name,
            language=language,
        )
        self.message_history: List[MessageAnalysis] = []

    def analyze_message(self, message: str, is_user: bool = True) -> MessageAnalysis:
        """
        Analyze a single message
        Returns validated MessageAnalysis with intent, sentiment, and routing
        """
        role = "user" if is_user else "assistant"

        # Detect intent
        intent = self._detect_intent(message)

        # Analyze sentiment
        sentiment = self._analyze_sentiment(message)

        # Generate routing decision (for user messages)
        routing = None
        if is_user:
            routing = self._generate_routing_decision(intent, sentiment)

        # Create validated message analysis
        analysis = MessageAnalysis(
            call_id=self.state.call_id,
            message=message,
            role=role,
            intent=intent,
            sentiment=sentiment,
            routing_decision=routing,
            requires_ticket=intent.intent == ConversationIntent.COMPLAINT,
            complaint_indicated=intent.intent == ConversationIntent.COMPLAINT,
            question_asked=self._has_question(message),
            contact_info_provided=self._has_contact_info(message),
        )

        # Store in history
        self.message_history.append(analysis)

        # Update conversation state
        self._update_state(analysis)

        return analysis

    def _detect_intent(self, message: str) -> IntentAnalysis:
        """Detect intent from message using Pydantic validation"""
        message_lower = message.lower()
        message_ar = message  # Keep original for Arabic

        # Define keywords for each intent (EN and AR)
        intent_keywords = {
            ConversationIntent.COMPLAINT: {
                "en": ["problem", "issue", "complaint", "broken", "error", "wrong", "bad", "not working"],
                "ar": ["مشكلة", "شكوى", "خطأ", "عطل", "سيء", "لا يعمل", "مشاكل"]
            },
            ConversationIntent.SALES_INTEREST: {
                "en": ["price", "cost", "quote", "offer", "interested", "buy", "purchase", "deal"],
                "ar": ["سعر", "تكلفة", "عرض", "مهتم", "شراء", "صفقة"]
            },
            ConversationIntent.SERVICE_INQUIRY: {
                "en": ["service", "information", "tell me about", "what is", "how", "explain"],
                "ar": ["خدمة", "معلومات", "شرح", "كيفية", "ما هو"]
            },
            ConversationIntent.TRAINING_INTEREST: {
                "en": ["training", "course", "learn", "education", "program"],
                "ar": ["تدريب", "دورة", "برنامج", "تعليم", "تعلم"]
            },
            ConversationIntent.BILLING_ISSUE: {
                "en": ["billing", "invoice", "payment", "charge", "money", "cost"],
                "ar": ["فاتورة", "دفع", "رسوم", "المال", "السعر"]
            },
            ConversationIntent.TECHNICAL_SUPPORT: {
                "en": ["technical", "bug", "crash", "not working", "error", "help"],
                "ar": ["تقني", "خلل", "يتعطل", "مساعدة", "مشكلة تقنية"]
            },
        }

        # Score each intent
        intent_scores: Dict[ConversationIntent, float] = {}

        for intent, keywords in intent_keywords.items():
            en_keywords = keywords.get("en", [])
            ar_keywords = keywords.get("ar", [])

            # Count matching keywords
            en_matches = sum(1 for kw in en_keywords if kw in message_lower)
            ar_matches = sum(1 for kw in ar_keywords if kw in message_ar)

            # Calculate confidence (0-1)
            total_keywords = len(en_keywords) + len(ar_keywords)
            matches = en_matches + ar_matches
            confidence = min(1.0, matches / max(1, total_keywords * 0.5))

            intent_scores[intent] = confidence

        # Get top intent
        top_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[top_intent]

        # If confidence is too low, default to general info
        if confidence < 0.2:
            top_intent = ConversationIntent.GENERAL_INFO
            confidence = 0.5

        # Collect keywords
        matched_keywords = []
        keywords_for_intent = intent_keywords.get(top_intent, {})
        for kw_list in keywords_for_intent.values():
            matched_keywords.extend([kw for kw in kw_list if kw in message_lower or kw in message_ar])

        return IntentAnalysis(
            intent=top_intent,
            confidence=confidence,
            keywords=matched_keywords,
            language=self.state.language,
            reasoning=f"Detected {top_intent.value} with {len(matched_keywords)} matching keywords"
        )

    def _analyze_sentiment(self, message: str) -> SentimentAnalysisResult:
        """Analyze sentiment from message"""
        message_lower = message.lower()

        # Sentiment indicators
        positive_words = ["good", "great", "excellent", "happy", "love", "amazing",
                         "جيد", "رائع", "ممتاز", "سعيد", "أحب"]
        negative_words = ["bad", "terrible", "hate", "angry", "frustrated", "worst",
                         "سيء", "فظيع", "غاضب", "محبط", "أسوأ"]
        frustrated_words = ["problem", "issue", "broken", "not working", "error",
                           "مشكلة", "عطل", "خطأ"]

        # Count indicators
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        frustrated_count = sum(1 for word in frustrated_words if word in message_lower)

        # Determine sentiment
        if frustrated_count > 0:
            sentiment = SentimentAnalysis.FRUSTRATED if frustrated_count > 1 else SentimentAnalysis.NEGATIVE
            confidence = min(1.0, frustrated_count * 0.3)
        elif negative_count > positive_count:
            sentiment = SentimentAnalysis.ANGRY if negative_count > 2 else SentimentAnalysis.NEGATIVE
            confidence = min(1.0, (negative_count - positive_count) * 0.3)
        elif positive_count > negative_count:
            sentiment = SentimentAnalysis.POSITIVE
            confidence = min(1.0, positive_count * 0.3)
        else:
            sentiment = SentimentAnalysis.NEUTRAL
            confidence = 0.5

        return SentimentAnalysisResult(
            sentiment=sentiment,
            confidence=confidence,
            emotion_indicators=[w for w in positive_words + negative_words + frustrated_words
                              if w in message_lower],
            reasoning=f"Detected {sentiment.value} based on {positive_count} positive, {negative_count} negative indicators"
        )

    def _generate_routing_decision(self, intent: IntentAnalysis, sentiment: SentimentAnalysisResult) -> RoutingDecision:
        """
        Generate routing decision based on intent and sentiment
        Using Pydantic model for validation
        """
        intent_type = intent.intent

        # Determine target persona
        if intent_type == ConversationIntent.COMPLAINT:
            target_persona = "complaints"
            priority = PriorityLevel.HIGH if sentiment.sentiment in [SentimentAnalysis.ANGRY, SentimentAnalysis.FRUSTRATED] else PriorityLevel.MEDIUM
            create_ticket = True
        elif intent_type == ConversationIntent.SALES_INTEREST:
            target_persona = "sales"
            priority = PriorityLevel.MEDIUM
            create_ticket = False
        elif intent_type == ConversationIntent.TRAINING_INTEREST:
            target_persona = "sales"  # Sales handles training inquiries
            priority = PriorityLevel.MEDIUM
            create_ticket = False
        elif intent_type in [ConversationIntent.TECHNICAL_SUPPORT, ConversationIntent.BILLING_ISSUE]:
            target_persona = "complaints"
            priority = PriorityLevel.HIGH
            create_ticket = True
        else:
            target_persona = "reception"
            priority = PriorityLevel.LOW
            create_ticket = False

        # Determine escalation
        escalation_needed = (
            sentiment.sentiment in [SentimentAnalysis.ANGRY] or
            priority == PriorityLevel.URGENT
        )

        return RoutingDecision(
            target_persona=target_persona,
            priority=priority,
            suggested_action=f"Route to {target_persona} agent",
            create_ticket=create_ticket,
            escalation_needed=escalation_needed,
            reasoning=f"Intent: {intent.intent.value}, Sentiment: {sentiment.sentiment.value}, Confidence: {intent.confidence:.2f}"
        )

    def _has_question(self, message: str) -> bool:
        """Check if message contains a question"""
        return "?" in message or any(word in message.lower() for word in ["what", "how", "why", "when", "where"])

    def _has_contact_info(self, message: str) -> bool:
        """Check if message contains contact information"""
        return any(indicator in message for indicator in ["@", "+966", "phone", "email"])

    def _update_state(self, analysis: MessageAnalysis):
        """Update conversation state with new message analysis"""
        self.state.message_count += 1
        if analysis.role == "user":
            self.state.user_message_count += 1

        # Update intent and sentiment
        if analysis.role == "user":
            self.state.last_intent = analysis.intent.intent
            self.state.last_sentiment = analysis.sentiment.sentiment

            # Update overall sentiment (exponential smoothing)
            if analysis.sentiment.sentiment == SentimentAnalysis.POSITIVE:
                self.state.overall_sentiment = SentimentAnalysis.POSITIVE
            elif analysis.sentiment.sentiment == SentimentAnalysis.NEGATIVE:
                self.state.overall_sentiment = SentimentAnalysis.NEGATIVE

        # Update personas used
        if analysis.routing_decision:
            persona = analysis.routing_decision.target_persona
            if persona not in self.state.personas_used:
                self.state.personas_used.append(persona)

        # Update escalation count
        if analysis.routing_decision and analysis.routing_decision.escalation_needed:
            self.state.escalation_count += 1

        # Update last activity
        self.state.last_activity_at = datetime.now()

    def get_conversation_analysis(self) -> Dict[str, Any]:
        """Get comprehensive conversation analysis"""
        return {
            "state": self.state.dict(),
            "message_analyses": [msg.dict() for msg in self.message_history],
            "summary": {
                "total_messages": self.state.message_count,
                "user_messages": self.state.user_message_count,
                "dominant_intent": self.state.last_intent.value if self.state.last_intent else None,
                "overall_sentiment": self.state.overall_sentiment.value,
                "personas_involved": self.state.personas_used,
                "escalations": self.state.escalation_count,
                "requires_follow_up": self.state.escalation_count > 0 or self.state.overall_sentiment == SentimentAnalysis.NEGATIVE,
            }
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "ConversationIntent",
    "SentimentAnalysis",
    "PriorityLevel",
    "IntentAnalysis",
    "SentimentAnalysisResult",
    "RoutingDecision",
    "ConversationState",
    "MessageAnalysis",
    "ConversationAnalyzer",
]
