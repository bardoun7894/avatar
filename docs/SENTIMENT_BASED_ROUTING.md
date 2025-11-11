# Sentiment-Based Routing for Multi-Assistant Call Center

## Overview

The Call Center uses **sentiment analysis** to intelligently route customers to the appropriate assistant:

- **Excited / Interested** → Route to **Sales Assistant** (Sarah)
- **Complaining / Negative** → Route to **Complaints Assistant** (Mohammed)
- **Neutral / General Inquiry** → Stay with **Reception Assistant** (Ahmed)

---

## Architecture

```
Customer Call
     ↓
[Reception Assistant - Ahmed]
     ↓
Analyze Sentiment
     ↓
┌────────┴────────┐
│                 │
│  Positive/      │  Negative/
│  Excited?       │  Complaining?
│                 │
↓                 ↓
[Sales - Sarah]   [Complaints - Mohammed]
```

---

## Implementation

### Step 1: Add Sentiment Analysis Module

Create: `callCenter/sentiment_analyzer.py`

```python
#!/usr/bin/env python3
"""
Sentiment Analysis for Call Routing
Analyzes customer messages to detect:
- Positive/Excited → Sales
- Negative/Complaining → Complaints
- Neutral → Reception
"""

import logging
from enum import Enum
from typing import Dict, Tuple
import re

logger = logging.getLogger(__name__)

class Sentiment(str, Enum):
    """Customer sentiment types"""
    POSITIVE = "positive"      # Excited, interested in buying
    NEGATIVE = "negative"      # Complaining, dissatisfied
    NEUTRAL = "neutral"        # General inquiry, information request


class Department(str, Enum):
    """Call center departments"""
    RECEPTION = "reception"
    SALES = "sales"
    COMPLAINTS = "complaints"


class SentimentAnalyzer:
    """Analyzes customer sentiment for intelligent routing"""

    def __init__(self):
        # Arabic keywords for sentiment detection
        self.positive_keywords_ar = [
            # Buying intent
            "شراء", "أريد", "أحتاج", "أرغب", "سعر", "كم", "تكلفة",
            # Interest
            "مهتم", "معجب", "رائع", "ممتاز", "جيد",
            # Services
            "خدمة", "عرض", "باقة", "منتج",
            # Positive emotions
            "سعيد", "راض", "ممتن"
        ]

        self.negative_keywords_ar = [
            # Complaints
            "شكوى", "مشكلة", "عطل", "خطأ", "غلط",
            # Dissatisfaction
            "غير راض", "سيء", "مزعج", "محبط",
            # Problems
            "لا يعمل", "معطل", "متأخر", "بطيء",
            # Emotions
            "غاضب", "محبط", "منزعج", "مستاء"
        ]

        # English keywords
        self.positive_keywords_en = [
            # Buying intent
            "buy", "purchase", "want", "need", "price", "cost", "how much",
            # Interest
            "interested", "like", "great", "excellent", "good",
            # Services
            "service", "offer", "package", "product",
            # Positive emotions
            "happy", "satisfied", "pleased"
        ]

        self.negative_keywords_en = [
            # Complaints
            "complaint", "problem", "issue", "error", "bug",
            # Dissatisfaction
            "unhappy", "bad", "terrible", "annoying", "frustrating",
            # Problems
            "not working", "broken", "delayed", "slow",
            # Emotions
            "angry", "frustrated", "upset", "disappointed"
        ]

    def analyze_message(self, text: str) -> Tuple[Sentiment, float]:
        """
        Analyze customer message and return sentiment with confidence score

        Args:
            text: Customer message in Arabic or English

        Returns:
            Tuple of (Sentiment, confidence_score)
            confidence_score: 0.0 to 1.0
        """

        text_lower = text.lower()

        # Count positive keywords
        positive_count = 0
        for keyword in self.positive_keywords_ar + self.positive_keywords_en:
            if keyword in text_lower:
                positive_count += 1

        # Count negative keywords
        negative_count = 0
        for keyword in self.negative_keywords_ar + self.negative_keywords_en:
            if keyword in text_lower:
                negative_count += 1

        # Calculate confidence
        total_keywords = positive_count + negative_count

        if total_keywords == 0:
            return Sentiment.NEUTRAL, 0.5

        # Determine sentiment
        if positive_count > negative_count:
            confidence = positive_count / total_keywords
            return Sentiment.POSITIVE, confidence

        elif negative_count > positive_count:
            confidence = negative_count / total_keywords
            return Sentiment.NEGATIVE, confidence

        else:
            return Sentiment.NEUTRAL, 0.5

    def analyze_with_openai(self, text: str, openai_client) -> Tuple[Sentiment, float]:
        """
        Use OpenAI GPT for advanced sentiment analysis

        Args:
            text: Customer message
            openai_client: OpenAI client instance

        Returns:
            Tuple of (Sentiment, confidence_score)
        """

        try:
            prompt = f"""
Analyze the sentiment of this customer message and determine their intent.

Message: "{text}"

Classify as:
- POSITIVE: Customer is interested in buying, excited about services, or showing positive interest
- NEGATIVE: Customer is complaining, dissatisfied, or has a problem
- NEUTRAL: General inquiry or information request

Respond with JSON:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "reason": "brief explanation"
}}
"""

            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert for customer service."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            import json
            result = json.loads(response.choices[0].message.content)

            sentiment_map = {
                "positive": Sentiment.POSITIVE,
                "negative": Sentiment.NEGATIVE,
                "neutral": Sentiment.NEUTRAL
            }

            sentiment = sentiment_map.get(result["sentiment"].lower(), Sentiment.NEUTRAL)
            confidence = float(result.get("confidence", 0.5))

            logger.info(f"OpenAI Sentiment: {sentiment} ({confidence:.2f}) - {result.get('reason', '')}")

            return sentiment, confidence

        except Exception as e:
            logger.error(f"OpenAI sentiment analysis failed: {e}")
            # Fallback to keyword-based
            return self.analyze_message(text)

    def get_department_for_sentiment(self, sentiment: Sentiment) -> Department:
        """
        Map sentiment to appropriate department

        Args:
            sentiment: Detected sentiment

        Returns:
            Department to route to
        """

        routing_map = {
            Sentiment.POSITIVE: Department.SALES,
            Sentiment.NEGATIVE: Department.COMPLAINTS,
            Sentiment.NEUTRAL: Department.RECEPTION
        }

        return routing_map.get(sentiment, Department.RECEPTION)


# Singleton instance
_analyzer = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


# Export
__all__ = [
    "Sentiment",
    "Department",
    "SentimentAnalyzer",
    "get_sentiment_analyzer"
]
```

---

### Step 2: Update call_center_agent.py with Sentiment Routing

```python
# call_center_agent.py - Add sentiment-based routing

from sentiment_analyzer import get_sentiment_analyzer, Sentiment, Department
from openai_personas import get_persona_manager, PersonaType
from openai import OpenAI

# Initialize
sentiment_analyzer = get_sentiment_analyzer()
persona_manager = get_persona_manager()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Track current department
current_department = Department.RECEPTION


async def analyze_and_route(text: str, assistant, language: str = "ar"):
    """
    Analyze customer message sentiment and route to appropriate assistant

    Args:
        text: Customer message
        assistant: Voice assistant instance
        language: Customer language (ar/en)
    """

    global current_department

    logger.info(f"📊 Analyzing message: {text[:50]}...")

    # Analyze sentiment using OpenAI
    sentiment, confidence = sentiment_analyzer.analyze_with_openai(text, openai_client)

    logger.info(f"💭 Sentiment: {sentiment.value} (confidence: {confidence:.2f})")

    # Get recommended department
    recommended_dept = sentiment_analyzer.get_department_for_sentiment(sentiment)

    # Only transfer if:
    # 1. Confidence is high enough (> 0.6)
    # 2. Recommended department is different from current
    # 3. Not neutral (stay with reception for neutral)
    if (confidence > 0.6 and
        recommended_dept != current_department and
        sentiment != Sentiment.NEUTRAL):

        logger.info(f"🔄 Routing from {current_department.value} → {recommended_dept.value}")

        await transfer_to_department(
            assistant,
            recommended_dept.value,
            language,
            reason=sentiment.value
        )

        current_department = recommended_dept

    else:
        logger.info(f"✅ Staying with {current_department.value}")


async def transfer_to_department(
    assistant,
    new_department: str,
    language: str = "ar",
    reason: str = None
):
    """Transfer call to different department based on sentiment"""

    logger.info(f"🔄 Transferring to {new_department} (reason: {reason})")

    # Map department to persona
    persona_map = {
        "reception": PersonaType.RECEPTION,
        "sales": PersonaType.SALES,
        "complaints": PersonaType.COMPLAINTS
    }

    persona_type = persona_map[new_department]
    persona_manager.set_current_persona(persona_type)

    # Get new system prompt
    new_prompt = persona_manager.get_system_prompt(persona_type, language)

    # Announce transfer with reason
    transfer_messages = {
        "positive": {
            "ar": "أرى أنك مهتم بخدماتنا! جاري تحويلك إلى قسم المبيعات...",
            "en": "I see you're interested in our services! Transferring you to Sales..."
        },
        "negative": {
            "ar": "أنا آسف لسماع ذلك. جاري تحويلك إلى قسم الشكاوى للمساعدة...",
            "en": "I'm sorry to hear that. Transferring you to Complaints for assistance..."
        }
    }

    if reason in transfer_messages:
        message = transfer_messages[reason][language]
        await assistant.say(message)

    # Update system prompt
    await assistant.update_context(
        llm.ChatMessage(role="system", content=new_prompt)
    )

    # Welcome from new department
    welcome_messages = {
        "sales": {
            "ar": "مرحباً! أنا سارة من قسم المبيعات. سأساعدك في اختيار الخدمة المناسبة.",
            "en": "Hello! I'm Sarah from Sales. I'll help you choose the right service."
        },
        "complaints": {
            "ar": "أهلاً بك. أنا محمد من قسم الشكاوى. سأستمع لمشكلتك وأساعدك في حلها.",
            "en": "Welcome. I'm Mohammed from Complaints. I'll listen and help resolve your issue."
        }
    }

    if new_department in welcome_messages:
        welcome = welcome_messages[new_department][language]
        await assistant.say(welcome)

    logger.info(f"✅ Transferred to {new_department}")


async def entrypoint(ctx: AgentSession):
    """Main agent entrypoint with sentiment-based routing"""

    logger.info(f"📞 Agent joining room: {ctx.room.name}")

    # Extract metadata
    room_metadata = ctx.room.metadata or "{}"
    import json
    try:
        metadata = json.loads(room_metadata)
        language = metadata.get("language", "ar")
    except:
        language = "ar"

    # Start with reception
    global current_department
    current_department = Department.RECEPTION

    logger.info(f"🎭 Starting with Reception (sentiment routing enabled)")

    # Get reception system prompt
    system_prompt = persona_manager.get_system_prompt(
        PersonaType.RECEPTION,
        language
    )

    # Initialize conversation
    initial_ctx = llm.ChatContext().add_messages(
        llm.ChatMessage(role="system", content=system_prompt),
        llm.ChatMessage(
            role="assistant",
            content="أهلاً وسهلاً بكم في أورنينا. أنا أحمد، كيف يمكنني مساعدتك؟"
        ),
    )

    # Create voice assistant
    opts = VoiceAssistantOptions(
        transcription=openai.STT(model="whisper-1"),
        chat=openai.LLM(model="gpt-4-turbo-preview"),
        tts=openai.TTS(model="tts-1", voice="alloy"),
        vad=silero.VAD.load(),
        allow_interruptions=True,
        auto_reconnect=True,
    )

    assistant = VoiceAssistantOptions.create(ctx, opts, initial_ctx)

    # Listen for user messages and analyze sentiment
    @assistant.on("user_speech_committed")
    async def on_user_speech(text: str):
        """Analyze sentiment when user speaks"""
        logger.info(f"👤 User said: {text}")
        await analyze_and_route(text, assistant, language)

    logger.info("🎙️ Starting voice assistant with sentiment routing...")
    await assistant.start()

    # Keep agent alive
    while ctx.room.is_connected:
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("🛑 Agent shutting down...")
            break

    logger.info("👋 Agent disconnected from room")
```

---

## Sentiment Detection Examples

### Example 1: Excited Customer → Sales

**Customer says:**
> "أريد شراء خدمة التسويق الرقمي، كم السعر؟"
> "I want to buy the digital marketing service, how much is the price?"

**Sentiment Analysis:**
- Keywords detected: "أريد" (want), "شراء" (buy), "السعر" (price)
- Sentiment: **POSITIVE** (confidence: 0.85)
- Action: Transfer to **Sales Assistant (Sarah)**

**Response:**
> "أرى أنك مهتم بخدماتنا! جاري تحويلك إلى قسم المبيعات..."
> "مرحباً! أنا سارة من قسم المبيعات. سأساعدك في اختيار الخدمة المناسبة."

---

### Example 2: Complaining Customer → Complaints

**Customer says:**
> "لدي مشكلة كبيرة، الخدمة لا تعمل منذ يومين!"
> "I have a big problem, the service hasn't been working for two days!"

**Sentiment Analysis:**
- Keywords detected: "مشكلة" (problem), "لا تعمل" (not working)
- Sentiment: **NEGATIVE** (confidence: 0.90)
- Action: Transfer to **Complaints Assistant (Mohammed)**

**Response:**
> "أنا آسف لسماع ذلك. جاري تحويلك إلى قسم الشكاوى للمساعدة..."
> "أهلاً بك. أنا محمد من قسم الشكاوى. سأستمع لمشكلتك وأساعدك في حلها."

---

### Example 3: General Inquiry → Stay with Reception

**Customer says:**
> "ما هي ساعات العمل؟"
> "What are your working hours?"

**Sentiment Analysis:**
- Keywords detected: None significant
- Sentiment: **NEUTRAL** (confidence: 0.5)
- Action: **Stay with Reception (Ahmed)**

**Response:**
> "ساعات العمل من الساعة 9 صباحاً حتى 6 مساءً..."

---

## Advanced Sentiment Analysis with GPT-4

For more accurate sentiment detection, the system can use GPT-4:

```python
# sentiment_analyzer.py
def analyze_with_openai(self, text: str, openai_client) -> Tuple[Sentiment, float]:
    """Use GPT-4 for advanced sentiment analysis"""

    prompt = f"""
Analyze this customer message for call center routing:

Message: "{text}"

Detect:
1. **Buying Intent** (excited, wants to purchase)
   - Keywords: want to buy, interested in service, how much, price
   → Route to SALES

2. **Complaint Intent** (dissatisfied, has problem)
   - Keywords: problem, not working, complaint, disappointed
   → Route to COMPLAINTS

3. **Neutral Inquiry** (just asking for information)
   - Keywords: what is, where is, when is, general questions
   → Stay with RECEPTION

Respond with:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "intent": "buying|complaining|inquiry",
    "reason": "brief explanation in Arabic/English"
}}
"""

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a sentiment analysis expert for Arabic/English customer service."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    # Parse and return result
    # ...
```

---

## Routing Logic

```
┌─────────────────────────────────────────────┐
│      Customer Message Received              │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│      Analyze Sentiment (Keyword or GPT-4)   │
│                                             │
│  Positive Keywords:                         │
│  - شراء (buy), أريد (want), سعر (price)     │
│  - interested, purchase, how much           │
│                                             │
│  Negative Keywords:                         │
│  - شكوى (complaint), مشكلة (problem)        │
│  - not working, disappointed, issue         │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
      ┌───────────┴───────────┐
      │                       │
      ↓                       ↓
  Positive?              Negative?
  (Confidence > 0.6)     (Confidence > 0.6)
      │                       │
      ↓                       ↓
┌─────────────┐         ┌──────────────┐
│   SALES     │         │  COMPLAINTS  │
│   (Sarah)   │         │  (Mohammed)  │
└─────────────┘         └──────────────┘
      │
      │    Neutral or Low Confidence
      ↓
┌─────────────┐
│  RECEPTION  │
│   (Ahmed)   │
└─────────────┘
```

---

## Configuration

### Environment Variables

```bash
# .env
# Sentiment Analysis Configuration
SENTIMENT_CONFIDENCE_THRESHOLD=0.6  # Minimum confidence to transfer
SENTIMENT_USE_OPENAI=true           # Use GPT-4 for analysis (more accurate)
SENTIMENT_FALLBACK_KEYWORDS=true    # Fallback to keywords if GPT fails
```

### Tuning Parameters

```python
# sentiment_analyzer.py

# Confidence threshold for routing (0.0 - 1.0)
# Higher = more conservative (fewer transfers)
# Lower = more aggressive (more transfers)
CONFIDENCE_THRESHOLD = 0.6

# Minimum keywords to trigger sentiment
MIN_KEYWORDS_FOR_TRANSFER = 2

# Cool-down period between transfers (seconds)
TRANSFER_COOLDOWN = 60  # Don't transfer again for 60s
```

---

## Testing

### Test Case 1: Sales Intent

```bash
# Input
"أريد شراء خدمة التسويق الرقمي، أنا مهتم جداً!"

# Expected
Sentiment: POSITIVE (0.85)
Route: RECEPTION → SALES
Response: "مرحباً! أنا سارة من قسم المبيعات..."
```

### Test Case 2: Complaint Intent

```bash
# Input
"الخدمة لا تعمل، أنا منزعج جداً من هذه المشكلة!"

# Expected
Sentiment: NEGATIVE (0.90)
Route: RECEPTION → COMPLAINTS
Response: "أنا آسف لسماع ذلك. أنا محمد من قسم الشكاوى..."
```

### Test Case 3: Neutral Inquiry

```bash
# Input
"ما هي الخدمات المتاحة لديكم؟"

# Expected
Sentiment: NEUTRAL (0.5)
Route: Stay with RECEPTION
Response: Ahmed answers with service information
```

---

## Monitoring

### Log Examples

```
📊 Analyzing message: أريد شراء خدمة...
💭 Sentiment: positive (confidence: 0.85)
🔄 Routing from reception → sales
✅ Transferred to sales

📊 Analyzing message: لدي مشكلة...
💭 Sentiment: negative (confidence: 0.90)
🔄 Routing from reception → complaints
✅ Transferred to complaints

📊 Analyzing message: ما هي ساعات العمل؟
💭 Sentiment: neutral (confidence: 0.5)
✅ Staying with reception
```

---

## Summary

**Intelligent Multi-Assistant Routing:**

1. **Customer speaks** → Message transcribed
2. **Sentiment analyzed** → Positive/Negative/Neutral
3. **Route intelligently:**
   - Excited/Buying → **Sales** (Sarah)
   - Complaining/Problem → **Complaints** (Mohammed)
   - General/Neutral → **Reception** (Ahmed)

**Benefits:**
- Automatic, intelligent routing
- No manual selection needed
- Better customer experience
- Efficient department utilization

---

**Document Created:** 2025-11-10
**Status:** Sentiment-Based Routing Guide Complete
