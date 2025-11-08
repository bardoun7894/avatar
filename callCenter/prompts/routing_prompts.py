#!/usr/bin/env python3
"""
Call Center Routing Prompts - Separate from Avatar
Bilingual prompts for Reception, Sales, and Complaints departments
Using Ornina company information
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DepartmentEnum(str, Enum):
    """Department routing options"""
    RECEPTION = "reception"
    SALES = "sales"
    COMPLAINTS = "complaints"


class IntentEnum(str, Enum):
    """Customer intent categories"""
    INQUIRY = "inquiry"  # General information
    SERVICE_INQUIRY = "service_inquiry"  # Asking about services
    TRAINING_INQUIRY = "training_inquiry"  # Asking about training
    COMPLAINT = "complaint"  # Has a problem
    CONSULTATION = "consultation"  # Wants consultation
    APPOINTMENT = "appointment"  # Wants to book appointment
    OTHER = "other"


class LanguageEnum(str, Enum):
    """Supported languages"""
    ARABIC = "ar"
    ENGLISH = "en"


# ============================================================================
# PYDANTIC MODELS FOR ROUTING
# ============================================================================

class CustomerInfo(BaseModel):
    """Customer information collected during reception"""
    name: Optional[str] = Field(None, description="Customer full name")
    phone: Optional[str] = Field(None, description="Customer phone number")
    email: Optional[str] = Field(None, description="Customer email address")
    company: Optional[str] = Field(None, description="Customer company name")
    language: LanguageEnum = Field(default=LanguageEnum.ARABIC)


class IntentDetection(BaseModel):
    """Detected customer intent and routing decision"""
    intent: IntentEnum = Field(description="Detected customer intent")
    department: DepartmentEnum = Field(description="Target department to route")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    keywords: List[str] = Field(default_factory=list, description="Keywords that triggered this intent")
    reasoning: str = Field(description="Explanation of the routing decision")


class RoutingDecision(BaseModel):
    """Final routing decision with all details"""
    call_id: str = Field(description="Unique call identifier")
    customer_info: CustomerInfo = Field(description="Customer information")
    intent_detection: IntentDetection = Field(description="Intent detection result")
    target_agent: Optional[str] = Field(None, description="Assigned agent ID if available")
    timestamp: str = Field(description="Routing timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# DEPARTMENT PERSONAS
# ============================================================================

class DepartmentPersona(BaseModel):
    """Persona information for each department"""
    department: DepartmentEnum = Field(description="Department")
    name_ar: str = Field(description="Assistant name in Arabic")
    name_en: str = Field(description="Assistant name in English")
    role_ar: str = Field(description="Role description in Arabic")
    role_en: str = Field(description="Role description in English")
    expertise_ar: List[str] = Field(description="Expertise areas in Arabic")
    expertise_en: List[str] = Field(description="Expertise areas in English")
    tone_ar: str = Field(description="Communication tone in Arabic")
    tone_en: str = Field(description="Communication tone in English")


# Department Personas (Different assistants for each department)
RECEPTION_PERSONA = DepartmentPersona(
    department=DepartmentEnum.RECEPTION,
    name_ar="فريق الاستقبال",
    name_en="Reception Team",
    role_ar="استقبال الزوار والعملاء وجمع بيانات اتصالهم",
    role_en="Welcome and assist incoming customers, collect contact information",
    expertise_ar=["جمع المعلومات", "توجيه العملاء", "التواصل الودود", "فهم احتياجات العملاء"],
    expertise_en=["Information gathering", "Customer routing", "Friendly communication", "Need identification"],
    tone_ar="ودود، احترافي، مساعد",
    tone_en="Friendly, professional, helpful"
)

SALES_PERSONA = DepartmentPersona(
    department=DepartmentEnum.SALES,
    name_ar="فريق المبيعات",
    name_en="Sales Team",
    role_ar="شرح الخدمات والعروض وتحويل الاستفسارات إلى فرص عمل",
    role_en="Explain services, present offers, convert inquiries into opportunities",
    expertise_ar=["شرح الخدمات", "تقديم العروض", "الإجابة على الأسئلة", "بناء الثقة", "إغلاق العروض"],
    expertise_en=["Service explanation", "Offer presentation", "Q&A handling", "Trust building", "Deal closing"],
    tone_ar="متحمس، إيجابي، مقنع، متخصص",
    tone_en="Enthusiastic, positive, persuasive, expert"
)

COMPLAINTS_PERSONA = DepartmentPersona(
    department=DepartmentEnum.COMPLAINTS,
    name_ar="فريق معالجة الشكاوى",
    name_en="Complaints Team",
    role_ar="الاستماع للعملاء وحل المشاكل وإنشاء تذاكر دعم",
    role_en="Listen to customers, resolve issues, create support tickets",
    expertise_ar=["الاستماع الفعّال", "حل المشاكل", "إدارة الأزمات", "التعاطف", "المتابعة"],
    expertise_en=["Active listening", "Problem solving", "Crisis management", "Empathy", "Follow-up"],
    tone_ar="متعاطف، هادئ، حازم، موثوق",
    tone_en="Empathetic, calm, firm, reliable"
)


# ============================================================================
# RECEPTION PROMPTS
# ============================================================================

class ReceptionPrompts:
    """Reception department prompts - Welcome, collect info, and route"""

    PERSONA = RECEPTION_PERSONA

    AR = {
        "greeting": "السلام عليكم! أهلاً بك في شركة أورنينا للذكاء الاصطناعي والحلول الرقمية. كيف بقدر ساعدك اليوم؟",

        "ask_name": "من فضلك، ما اسمك الكامل؟",
        "invalid_name": "عذراً، لم أفهم الاسم. يرجى تكرار اسمك من فضلك.",
        "name_confirmed": "شكراً {name}",

        "ask_phone": "يرجى إدخال أو نطق رقم هاتفك.",
        "invalid_phone": "عذراً، رقم الهاتف غير صحيح. يرجى تكرار الرقم.",
        "phone_confirmed": "شكراً، تم تسجيل رقمك: {phone}",

        "ask_email": "ما هو بريدك الإلكتروني؟",
        "invalid_email": "عذراً، البريد الإلكتروني غير صحيح. يرجى تكرار البريد.",
        "email_optional": "إذا كان لديك بريد إلكتروني، يمكنك إخبارنا، وإلا يمكنك النقر على تخطي.",

        "ask_intent": "حسناً، حكي لي ماذا تحتاج؟ هل لديك استفسار عن خدمة معينة أم لديك مشكلة؟",

        "service_inquiry_detected": "فهمت، أنت مهتم بـ {service}. سيتم توصيلك بقسم المبيعات المتخصص.",
        "complaint_detected": "فهمت، عندك مشكلة. سيتم توصيلك بقسم معالجة الشكاوى.",
        "training_inquiry_detected": "فهمت، أنت مهتم بالتدريب. سيتم توصيلك بقسم المبيعات للحصول على التفاصيل.",
        "information_only": "حسناً، ساشرح لك معلومات عن الشركة.",

        "routing_to_sales": "شكراً على البيانات. سيتم توجيهك الآن إلى قسم المبيعات. يرجى الانتظار قليلاً.",
        "routing_to_complaints": "شكراً على البيانات. سيتم توجيهك الآن إلى قسم معالجة الشكاوى. يرجى الانتظار.",
        "hold_message": "شكراً على انتظارك. سيتم الرد عليك قريباً.",

        "max_retries": "عذراً، لم نتمكن من جمع البيانات. سيتم توصيلك بممثل العملاء.",
        "goodbye": "شكراً لتواصلك معنا. فريقنا سيتواصل معك قريباً. وداعاً!",
    }

    EN = {
        "greeting": "Hello! Welcome to Ornina - AI Solutions & Digital Services. How can I help you today?",

        "ask_name": "Please tell me your full name.",
        "invalid_name": "Sorry, I didn't understand the name. Please repeat your name.",
        "name_confirmed": "Thank you {name}",

        "ask_phone": "Please provide your phone number.",
        "invalid_phone": "Sorry, the phone number is invalid. Please try again.",
        "phone_confirmed": "Thank you, your number is recorded: {phone}",

        "ask_email": "What is your email address?",
        "invalid_email": "Sorry, the email is invalid. Please try again.",
        "email_optional": "If you have an email, please share it. Otherwise, you can skip.",

        "ask_intent": "Alright, tell me what you need. Do you have a question about a service or a problem?",

        "service_inquiry_detected": "I understand, you're interested in {service}. You'll be connected to our Sales department.",
        "complaint_detected": "I understand you have an issue. You'll be connected to our Complaints department.",
        "training_inquiry_detected": "I understand you're interested in training. You'll be connected to our Sales team.",
        "information_only": "Alright, let me tell you about our company.",

        "routing_to_sales": "Thank you for the information. You'll now be connected to our Sales department. Please wait.",
        "routing_to_complaints": "Thank you for the information. You'll now be connected to our Complaints department. Please wait.",
        "hold_message": "Thank you for your patience. An agent will be with you shortly.",

        "max_retries": "Sorry, we couldn't collect the information. An agent will help you.",
        "goodbye": "Thank you for contacting us. Our team will reach out to you soon. Goodbye!",
    }

    @classmethod
    def get(cls, language: str, key: str, **kwargs) -> str:
        """Get prompt by language and key, with placeholder substitution"""
        prompts = cls.EN if language.lower() == "en" else cls.AR
        message = prompts.get(key, "")
        if kwargs:
            return message.format(**kwargs)
        return message


# ============================================================================
# SALES PROMPTS
# ============================================================================

class SalesPrompts:
    """Sales department prompts - Explain services, handle inquiries"""

    PERSONA = SALES_PERSONA

    AR = {
        "welcome": "السلام عليكم! أنا من قسم المبيعات. شكراً لاختيارك أورنينا.",

        "service_explanation": "نحن نقدم {count} خدمات متخصصة:",
        "service_list_intro": "اسمح لي أن أشرح لك خدماتنا الرئيسية:",

        "service_ai_call_center": "نظام ذكي للرد التلقائي على العملاء 24/7 - يفهم، يحلل، ويحل المشاكل بصوت طبيعي.",
        "service_film_production": "إنتاج محتوى بصري احترافي بتكلفة منخفضة - سيناريو، شخصيات، مشاهد، مونتاج كاملة.",
        "service_ai_ads": "إعلانات ذكية مخصصة لكل منصة (TikTok, Instagram, YouTube) مع تحليل الأداء.",
        "service_animation": "رسوم متحركة احترافية - شخصيات، بيئات، مؤثرات بصرية متقدمة.",
        "service_digital_platform": "منصة رقمية شاملة - فيديوهات، أكواد، صور، محادثات AI في أداة واحدة.",
        "service_web_design": "مواقع متجاوبة وسريعة - تصميم UI/UX حديث وبرمجة متكاملة.",

        "ask_service_interest": "أي من هذه الخدمات تهمك أكتر؟ أو في خدمة محددة تريد تعرف عنها أكتر؟",

        "budget_question": "لنتحدث عن الميزانية - هل لديك ميزانية معينة في بالك؟",
        "timeline_question": "ومتى تحتاج لإنجاز هذا المشروع؟",

        "create_opportunity": "حسناً، سأنشئ لك فرصة عمل وسيتواصل معك الفريق قريباً لمناقشة التفاصيل.",
        "collect_more_info": "دعني أجمع بعض المعلومات الإضافية للفريق.",

        "offer_consultation": "هل تود حجز استشارة مجانية مع متخصص يناقش معك احتياجاتك بالتفصيل؟",
        "consultation_offered": "رائع! سيتم التواصل معك لتحديد موعد مناسب.",

        "closing": "شكراً على الوقت. فريقنا سيتواصل معك خلال 24 ساعة. أتطلع للعمل معك!",
    }

    EN = {
        "welcome": "Hello! I'm from the Sales department. Thank you for choosing Ornina.",

        "service_explanation": "We offer {count} specialized services:",
        "service_list_intro": "Let me explain our main services:",

        "service_ai_call_center": "Smart 24/7 automatic response system - understands, analyzes, and solves problems with natural voice.",
        "service_film_production": "Professional visual content production - screenplay, characters, scenes, full editing.",
        "service_ai_ads": "Smart ads customized for each platform (TikTok, Instagram, YouTube) with performance analysis.",
        "service_animation": "Professional animations - characters, environments, advanced visual effects.",
        "service_digital_platform": "Comprehensive digital platform - videos, code, images, AI chat in one tool.",
        "service_web_design": "Responsive and fast websites - modern UI/UX design and integrated programming.",

        "ask_service_interest": "Which of these services interests you most? Or is there a specific service you'd like to know more about?",

        "budget_question": "Let's talk about budget - do you have a budget range in mind?",
        "timeline_question": "And when do you need this project completed?",

        "create_opportunity": "Alright, I'll create an opportunity for you and our team will contact you soon to discuss details.",
        "collect_more_info": "Let me collect some additional information for the team.",

        "offer_consultation": "Would you like to book a free consultation with a specialist to discuss your needs in detail?",
        "consultation_offered": "Great! We'll contact you to schedule a convenient time.",

        "closing": "Thank you for your time. Our team will reach out within 24 hours. Looking forward to working with you!",
    }

    @classmethod
    def get(cls, language: str, key: str, **kwargs) -> str:
        """Get prompt by language and key, with placeholder substitution"""
        prompts = cls.EN if language.lower() == "en" else cls.AR
        message = prompts.get(key, "")
        if kwargs:
            return message.format(**kwargs)
        return message


# ============================================================================
# COMPLAINTS PROMPTS
# ============================================================================

class ComplaintsPrompts:
    """Complaints department prompts - Understand issues, create tickets"""

    PERSONA = COMPLAINTS_PERSONA

    AR = {
        "welcome": "السلام عليكم! أنا من قسم معالجة الشكاوى. أنا هنا لمساعدتك.",

        "ask_issue": "من فضلك، حكي لي عن المشكلة. ما هي بالتحديد؟",
        "issue_clarification": "حسناً، فهمت. ممكن تعطيني المزيد من التفاصيل؟",

        "ask_impact": "هل هذه المشكلة تؤثر على عملك أم الخدمة المقدمة؟",

        "priority_urgent": "فهمت أن هذه مشكلة عاجلة جداً. سنعطيها الأولوية القصوى.",
        "priority_normal": "حسناً، سنتعامل مع هذا بسرعة.",

        "create_ticket": "حسناً، سأنشئ لك تذكرة دعم برقم {ticket_id} وسيتابع معك فريق مخصص.",

        "assign_agent": "تم إسناد قضيتك إلى {agent_name}. سيتواصل معك قريباً.",
        "escalate_message": "هذه القضية تحتاج متابعة متقدمة. سيتواصل معك مدير الفريق.",

        "resolution_timeline": "سنعمل على حل هذا في أسرع وقت. ستسمع منا خلال {hours} ساعات.",

        "collect_contact": "للتأكد من التواصل معك بسهولة، ممكن نؤكد رقم هاتفك {phone} وبريدك {email}؟",

        "closing": "شكراً على صبرك. سنحل هذا للك. رقم التذكرة: {ticket_id}",
    }

    EN = {
        "welcome": "Hello! I'm from the Complaints department. I'm here to help you.",

        "ask_issue": "Please tell me about the problem. What exactly is happening?",
        "issue_clarification": "I understand. Can you give me more details?",

        "ask_impact": "Is this affecting your business or the service provided?",

        "priority_urgent": "I understand this is very urgent. We'll give it top priority.",
        "priority_normal": "Alright, we'll handle this quickly.",

        "create_ticket": "Alright, I'm creating a support ticket number {ticket_id} for you. A dedicated team will follow up.",

        "assign_agent": "Your case has been assigned to {agent_name}. They'll contact you soon.",
        "escalate_message": "This needs advanced attention. A team manager will contact you.",

        "resolution_timeline": "We'll work on resolving this ASAP. You'll hear from us within {hours} hours.",

        "collect_contact": "To ensure we can contact you easily, can we confirm your phone {phone} and email {email}?",

        "closing": "Thank you for your patience. We'll resolve this for you. Ticket number: {ticket_id}",
    }

    @classmethod
    def get(cls, language: str, key: str, **kwargs) -> str:
        """Get prompt by language and key, with placeholder substitution"""
        prompts = cls.EN if language.lower() == "en" else cls.AR
        message = prompts.get(key, "")
        if kwargs:
            return message.format(**kwargs)
        return message


# ============================================================================
# INTENT DETECTION KEYWORDS
# ============================================================================

class IntentDetectionRules:
    """Rules to detect customer intent from messages"""

    SERVICE_INQUIRY_KEYWORDS = {
        "ar": [
            "خدمة", "خدمات", "تقدمون", "عندكم", "في عندكم",
            "Call Center", "أفلام", "إعلانات", "تصميم", "برمجة",
            "تدريب", "دورة", "كورس", "أنيميشن", "ويب",
        ],
        "en": [
            "service", "services", "offer", "do you have", "what do you offer",
            "call center", "film", "ads", "design", "programming",
            "training", "course", "animation", "web", "development",
        ]
    }

    COMPLAINT_KEYWORDS = {
        "ar": [
            "شكوى", "مشكلة", "مشاكل", "خطأ", "مش شغال",
            "ما اشتغل", "عم أواجه", "صعوبة", "تأخير", "متأخر",
            "ما استقبلت", "ما تسلمت", "رداء", "سيء", "سيئة",
        ],
        "en": [
            "complaint", "problem", "issue", "error", "not working",
            "doesn't work", "facing", "difficulty", "delay", "late",
            "didn't receive", "poor", "bad", "broken", "fault",
        ]
    }

    TRAINING_KEYWORDS = {
        "ar": [
            "تدريب", "دورة", "كورس", "تعليم", "أتعلم",
            "احترافي", "متخصص", "برنامج", "مستوى", "ساعات",
        ],
        "en": [
            "training", "course", "learn", "education", "program",
            "professional", "specialist", "hours", "level", "bootcamp",
        ]
    }

    @classmethod
    def detect_intent(cls, message: str, language: str = "ar") -> IntentEnum:
        """Detect customer intent from message"""
        message_lower = message.lower()

        # Check for complaints first (highest priority)
        complaint_keywords = cls.COMPLAINT_KEYWORDS.get(language, [])
        if any(keyword in message_lower for keyword in complaint_keywords):
            return IntentEnum.COMPLAINT

        # Check for training
        training_keywords = cls.TRAINING_KEYWORDS.get(language, [])
        if any(keyword in message_lower for keyword in training_keywords):
            return IntentEnum.TRAINING_INQUIRY

        # Check for service inquiry
        service_keywords = cls.SERVICE_INQUIRY_KEYWORDS.get(language, [])
        if any(keyword in message_lower for keyword in service_keywords):
            return IntentEnum.SERVICE_INQUIRY

        # Default to inquiry
        return IntentEnum.INQUIRY


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_by_intent(intent: IntentEnum) -> DepartmentEnum:
    """Route customer to department based on intent"""
    routing_map = {
        IntentEnum.COMPLAINT: DepartmentEnum.COMPLAINTS,
        IntentEnum.SERVICE_INQUIRY: DepartmentEnum.SALES,
        IntentEnum.TRAINING_INQUIRY: DepartmentEnum.SALES,
        IntentEnum.CONSULTATION: DepartmentEnum.SALES,
        IntentEnum.APPOINTMENT: DepartmentEnum.SALES,
        IntentEnum.INQUIRY: DepartmentEnum.RECEPTION,
        IntentEnum.OTHER: DepartmentEnum.RECEPTION,
    }
    return routing_map.get(intent, DepartmentEnum.RECEPTION)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "DepartmentEnum",
    "IntentEnum",
    "LanguageEnum",
    "CustomerInfo",
    "IntentDetection",
    "RoutingDecision",
    "DepartmentPersona",
    "RECEPTION_PERSONA",
    "SALES_PERSONA",
    "COMPLAINTS_PERSONA",
    "ReceptionPrompts",
    "SalesPrompts",
    "ComplaintsPrompts",
    "IntentDetectionRules",
    "route_by_intent",
]
