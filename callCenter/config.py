#!/usr/bin/env python3
"""
Call Center Configuration and Rules
Defines behavior rules that override avatary agent behavior
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()


# ============================================================================
# CONFIG CLASS (for api.py compatibility)
# ============================================================================

class CallCenterConfig:
    """Call Center Configuration object"""
    def __init__(self):
        pass  # All config is module-level constants


# ============================================================================
# CALL CENTER MODE CONFIGURATION
# ============================================================================

CALL_CENTER_MODE = os.getenv("CALL_CENTER_MODE", "enabled").lower() == "enabled"
CALL_CENTER_ENABLED = CALL_CENTER_MODE

# ============================================================================
# ORNINA COMPANY INFORMATION (Same as Avatar System)
# ============================================================================

COMPANY_NAME = os.getenv("COMPANY_NAME", "أورنينا")
COMPANY_NAME_EN = os.getenv("COMPANY_NAME_EN", "Ornina")
COMPANY_NAME_FULL = "شركة أورنينا للذكاء الاصطناعي والحلول الرقمية"
COMPANY_NAME_FULL_EN = "Ornina - AI Solutions & Digital Services"

# Contact Information
COMPANY_ADDRESS = "سوريا - دمشق - المزرعة - مقابل وزارة التربية"
COMPANY_ADDRESS_EN = "Syria - Damascus - Al Mezzeh - opposite Ministry of Education"
COMPANY_PHONE = "3349028"
COMPANY_PHONE_INTL = "+963-11-3349028"

# Social Media
COMPANY_SOCIAL_MEDIA = {
    "tiktok": "@ornina.official",
    "facebook": "@orninaofficial",
    "youtube": "@orninaofficial",
    "instagram": "@ornina.official"
}

# Services (6 main services from Avatar)
COMPANY_SERVICES = [
    {
        "id": "ai_call_center",
        "name": "Call Center بالذكاء الاصطناعي",
        "name_en": "AI Call Center",
        "description_ar": "نظام ذكي للرد التلقائي على العملاء 24 ساعة على 7 أيام يفهم، يحلل، ويحل المشاكل بصوت طبيعي",
        "description_en": "24/7 Smart automatic response system that understands, analyzes, and solves problems with natural voice",
        "benefits": [
            "استجابة فوری",
            "توفر التكاليف",
            "تحليل ذكاء أعمال"
        ]
    },
    {
        "id": "film_production",
        "name": "إنتاج الأفلام والمسلسلات بالذكاء الاصطناعي",
        "name_en": "AI Film & Series Production",
        "description_ar": "إنتاج محتوى بصري احترافي بتكلفة منخفضة - كتابة سيناريو، تصميم شخصيات، مشاهد، مونتاج",
        "description_en": "Professional visual content production at low cost - screenplay writing, character design, scenes, editing",
        "benefits": [
            "محتوى احترافي",
            "تكلفة منخفضة",
            "إنتاج سريع"
        ]
    },
    {
        "id": "ai_ads",
        "name": "الإعلانات الذكية بالذكاء الاصطناعي",
        "name_en": "AI Smart Ads",
        "description_ar": "إعلانات قصيرة مخصصة لكل منصة (TikTok, Instagram, YouTube) مع تحليل أداء وتحسين تلقائي",
        "description_en": "Short ads customized for each platform with performance analysis and automatic improvement",
        "benefits": [
            "إنتاج سريع 24-48 ساعة",
            "تحسين مستمر",
            "متوافق مع جميع المنصات"
        ]
    },
    {
        "id": "animation_2d_3d",
        "name": "الأنيميشن 2D/3D بالذكاء الاصطناعي",
        "name_en": "AI 2D/3D Animation",
        "description_ar": "رسوم متحركة احترافية للعلامات التجارية - شخصيات كرتونية، بيئات، مؤثرات بصرية",
        "description_en": "Professional animations for brands - cartoon characters, environments, visual effects",
        "benefits": [
            "شخصيات احترافية",
            "بيئات متقنة",
            "مؤثرات بصرية متقدمة"
        ]
    },
    {
        "id": "digital_platform",
        "name": "المنصة الرقمية الشاملة",
        "name_en": "Comprehensive Digital Platform",
        "description_ar": "أداة واحدة لتوليد: فيديوهات، أكواد برمجية، صور، محادثات AI - مناسبة للشركات والمبدعين",
        "description_en": "One tool to generate videos, code, images, AI chat - suitable for companies and creators",
        "benefits": [
            "أداة واحدة شاملة",
            "واجهة سهلة",
            "نتائج احترافية"
        ]
    },
    {
        "id": "web_design_dev",
        "name": "تصميم وبرمجة المواقع Front/Back End بالذكاء الاصطناعي",
        "name_en": "AI Website Design & Development",
        "description_ar": "مواقع متجاوبة، سريعة، آمنة مع تصميم UI/UX حديث وبرمجة متكاملة",
        "description_en": "Responsive, fast, secure websites with modern UI/UX design and integrated programming",
        "benefits": [
            "موقع متجاوب",
            "أداء سريع",
            "أمان عالي"
        ]
    }
]

# Training Programs (6 programs from Avatar)
COMPANY_TRAINING_PROGRAMS = [
    {
        "id": "digital_marketing",
        "name": "احتراف التسويق الرقمي باستخدام أدوات الذكاء الاصطناعي",
        "name_en": "Digital Marketing Mastery with AI Tools",
        "hours": 45,
        "level": "مبتدئ/متوسط",
        "description": "Prompt Engineering، صناعة المحتوى، استراتيجيات السوشيال ميديا، SEO، الإعلانات المدفوعة",
        "outcome": "بناء حملة تسويقية كاملة باستخدام AI"
    },
    {
        "id": "film_production_course",
        "name": "صناعة الأفلام الرقمية باستخدام الذكاء الاصطناعي",
        "name_en": "Digital Film Production with AI",
        "hours": 30,
        "level": "مبتدئ/متوسط",
        "description": "كتابة السيناريو، تصميم الشخصيات، إنتاج الفيديو، المونتاج والمؤثرات",
        "outcome": "إنتاج فيلم قصير كامل"
    },
    {
        "id": "ui_ux_design",
        "name": "تصميم UI/UX باستخدام الذكاء الاصطناعي",
        "name_en": "UI/UX Design with AI",
        "hours": 30,
        "level": "مبتدئ/متوسط",
        "description": "أساسيات تجربة المستخدم، تصميم الواجهات، Figma وأدوات AI",
        "outcome": "تصميم تطبيق موبايل أو موقع كامل"
    },
    {
        "id": "coding_basics",
        "name": "الأساسيات وتعلم توليد الأكواد باستخدام الذكاء الاصطناعي",
        "name_en": "Coding Fundamentals with AI Code Generation",
        "hours": 30,
        "level": "مبتدئ",
        "description": "Python، JavaScript، قواعد البيانات، استخدام GitHub Copilot وأدوات AI",
        "outcome": "بناء تطبيق ويب كامل"
    },
    {
        "id": "fashion_design",
        "name": "تصميم الأزياء الاحترافي باستخدام أدوات الذكاء الاصطناعي",
        "name_en": "Professional Fashion Design with AI Tools",
        "hours": 10,
        "level": "مبتدئ",
        "description": "تصميم أزياء رقمية، تجربة افتراضية، إنتاج كتالوج رقمي",
        "outcome": "مجموعة أزياء كاملة"
    },
    {
        "id": "web_design_course",
        "name": "تصميم وبرمجة مواقع الإنترنت باستخدام الذكاء الاصطناعي",
        "name_en": "Web Design & Development with AI",
        "hours": 30,
        "level": "مبتدئ/متوسط",
        "description": "HTML، CSS، JavaScript، استخدام AI في التصميم والبرمجة",
        "outcome": "موقع إلكتروني احترافي كامل"
    }
]

# Business Hours
BUSINESS_HOURS_START = os.getenv("BUSINESS_HOURS_START", "09:00")
BUSINESS_HOURS_END = os.getenv("BUSINESS_HOURS_END", "18:00")
BUSINESS_HOURS_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]


# ============================================================================
# IVR & ROUTING CONFIGURATION
# ============================================================================

# IVR Configuration
IVR_MAX_RETRIES = int(os.getenv("IVR_MAX_RETRIES", "3"))
IVR_TIMEOUT_SECONDS = int(os.getenv("IVR_TIMEOUT_SECONDS", "30"))
IVR_CONFIRMATION_RETRIES = int(os.getenv("IVR_CONFIRMATION_RETRIES", "2"))

# Default Department if routing fails
DEFAULT_DEPARTMENT = "reception"

# Departments configuration
DEPARTMENTS_CONFIG = {
    "reception": {
        "name_ar": "الاستقبال",
        "name_en": "Reception",
        "description_ar": "قسم استقبال المكالمات الأولية وجمع البيانات",
        "description_en": "Initial call reception and data collection",
        "priority": 1,
    },
    "sales": {
        "name_ar": "المبيعات",
        "name_en": "Sales",
        "description_ar": "قسم المبيعات والعروض",
        "description_en": "Sales and offers department",
        "priority": 2,
    },
    "complaints": {
        "name_ar": "الشكاوى",
        "name_en": "Complaints",
        "description_ar": "قسم معالجة الشكاوى والمشاكل",
        "description_en": "Complaints and issues department",
        "priority": 3,
    },
}


# ============================================================================
# RULES ENGINE CONFIGURATION
# ============================================================================

# Rules that determine behavior based on conditions
CALL_CENTER_RULES = {
    # Reception Rules
    "reception_rules": {
        # Collect customer data
        "require_name": True,
        "require_phone": True,
        "require_email": True,
        "require_service_type": True,

        # Validation rules
        "phone_min_length": 8,
        "email_validation": True,
        "name_min_length": 2,

        # Confirmation
        "require_data_confirmation": True,
        "confirmation_retries": 2,

        # Routing logic
        "auto_route_to_sales_keywords": ["بيع", "شراء", "سعر", "عرض", "منتج", "buy", "purchase", "price", "offer", "product"],
        "auto_route_to_complaints_keywords": ["شكوى", "مشكلة", "مشكل", "خطأ", "complaint", "issue", "problem", "error"],
    },

    # Sales Rules
    "sales_rules": {
        # Data collection
        "collect_service_details": True,
        "collect_budget": True,

        # Bot handling
        "bot_handles_simple_inquiries": True,
        "simple_inquiry_keywords": ["السعر", "المنتجات", "الخدمات", "price", "products", "services"],

        # Transfer conditions
        "transfer_on_complex_inquiry": True,
        "transfer_keywords": ["خاص", "مخصص", "عرض خاص", "custom", "special"],

        # FAQ responses
        "enable_faq_responses": True,
    },

    # Complaints Rules
    "complaints_rules": {
        # Data collection
        "collect_complaint_type": True,
        "collect_complaint_details": True,

        # Ticket creation
        "auto_create_ticket": True,
        "ticket_priority_urgent_keywords": ["عاجل", "حرج", "طوارئ", "urgent", "critical", "emergency"],

        # Transfer conditions
        "auto_transfer_complex_complaints": True,
        "always_show_agent_customer_info": True,
    },

    # General Rules
    "general_rules": {
        # Language handling
        "auto_detect_language": True,
        "default_language": "ar",
        "fallback_language": "en",

        # Call handling
        "save_transcript": True,
        "transcript_format": "text",  # "text" only, no audio recording

        # Timeouts
        "call_timeout_minutes": 30,
        "inactivity_timeout_minutes": 5,

        # Queue management
        "max_queue_size": 100,
        "max_wait_time_minutes": 10,
    }
}


# ============================================================================
# OVERRIDE RULES FOR AVATARY AGENT
# ============================================================================

# When call center mode is enabled, these rules override avatary behavior
AVATARY_OVERRIDES = {
    # Disable avatar visual features in call center
    "disable_avatar_display": True,
    "disable_face_recognition": False,  # Keep for agent benefits
    "disable_visual_context": True,

    # Change conversation behavior
    "use_call_center_prompts": True,
    "use_ivr_flow": True,
    "collect_structured_data": True,

    # Database logging
    "log_to_call_center_db": True,
    "create_tickets_on_complaints": True,

    # Disable non-essential features
    "disable_tavus_avatar": True,
    "disable_video_response": True,
}


# ============================================================================
# PROMPTS & MESSAGES
# ============================================================================

# Welcome messages
WELCOME_MESSAGE_AR = f"أهلاً وسهلاً بكم في {COMPANY_NAME}. سنقوم أولاً بجمع بعض المعلومات لتقديم خدمة أفضل."
WELCOME_MESSAGE_EN = f"Welcome to {COMPANY_NAME_EN}. We will first collect some information to serve you better."

# Guided data collection messages
PROMPTS_AR = {
    "greeting": WELCOME_MESSAGE_AR,
    "ask_name": "من فضلك، ما اسمك الكامل؟",
    "ask_phone": "يرجى إدخال أو نطق رقم هاتفك.",
    "ask_email": "ما هو بريدك الإلكتروني؟",
    "ask_service_type": "ما نوع الخدمة التي تحتاجها؟",
    "confirm_data": "للتأكيد، اسمك {name}، رقم هاتفك {phone}، بريدك {email}، والخدمة المطلوبة {service_type}؟ اضغط 1 لتأكيد أو 2 لتعديل.",
    "routing_to_sales": "سيتم توجيهك إلى قسم المبيعات. يرجى الانتظار.",
    "routing_to_complaints": "سيتم توجيهك إلى قسم معالجة الشكاوى. يرجى الانتظار.",
    "invalid_input": "عذراً، لم أفهم إجابتك. يرجى المحاولة مرة أخرى.",
    "max_retries": "عذراً، لم نتمكن من جمع البيانات. سيتم توصيلك بممثل العملاء.",
    "hold_message": "شكراً على انتظارك. سيكون متاح قريباً.",
}

PROMPTS_EN = {
    "greeting": WELCOME_MESSAGE_EN,
    "ask_name": "Please tell me your full name.",
    "ask_phone": "Please enter or say your phone number.",
    "ask_email": "What is your email address?",
    "ask_service_type": "What type of service do you need?",
    "confirm_data": "To confirm, your name is {name}, phone number {phone}, email {email}, and requested service is {service_type}? Press 1 to confirm or 2 to edit.",
    "routing_to_sales": "You will be routed to the Sales department. Please wait.",
    "routing_to_complaints": "You will be routed to the Complaints department. Please wait.",
    "invalid_input": "Sorry, I didn't understand your answer. Please try again.",
    "max_retries": "Sorry, we couldn't collect the information. You will be connected to a customer representative.",
    "hold_message": "Thank you for waiting. An agent will be available soon.",
}


# ============================================================================
# DATABASE CONFIGURATION FOR CALL CENTER
# ============================================================================

# Supabase configuration (same as avatary)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Table names in PostgreSQL
DB_TABLES = {
    "calls": "calls",
    "tickets": "tickets",
    "agents": "agents",
    "customers": "customers",
    "transcripts": "call_transcripts",
    "tickets_history": "tickets_history",
}


# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    # CRM System
    "enable_crm": True,
    "enable_ticket_system": True,
    "enable_auto_ticket_creation": True,

    # Analytics
    "enable_analytics": True,
    "enable_realtime_dashboard": True,

    # Queue Management
    "enable_queue_management": True,
    "enable_call_routing": True,

    # Agent Dashboard
    "enable_agent_dashboard": True,
    "enable_agent_transfer": True,

    # Transcript
    "enable_transcript_saving": True,
    "transcript_format": "text",  # "text" only

    # IVR
    "enable_ivr": True,
    "enable_dtmf_input": False,  # Web-based only for now
    "enable_menu_navigation": True,
}


# ============================================================================
# VOICE/TTS CONFIGURATION
# ============================================================================

# TTS Settings
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE_DEFAULT = "nova"  # Best for Arabic and English

# Voice mapping by language
TTS_VOICE_MAP = {
    "ar": "nova",      # Arabic
    "en": "nova",      # English
    "default": "nova"  # Fallback
}

# Audio output settings
AUDIO_OUTPUT_FORMAT = "mp3"
AUDIO_OUTPUT_SAMPLE_RATE = 24000

# Fallback TTS if OpenAI fails
FALLBACK_TTS_ENABLED = True
FALLBACK_TTS_SERVICE = "elevenlabs"  # Using ElevenLabs as fallback

# Voice activity detection
VAD_ENABLED = True
VAD_THRESHOLD = 0.5


# ============================================================================
# INTEGRATION SETTINGS
# ============================================================================

# API Configuration
API_PORT = int(os.getenv("CALL_CENTER_API_PORT", "8001"))
API_HOST = os.getenv("CALL_CENTER_API_HOST", "0.0.0.0")

# WebSocket configuration for real-time updates
WEBSOCKET_ENABLED = True
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8002"))

# Log configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("CALL_CENTER_LOG_FILE", "logs/call_center.log")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_prompts(language: str = "ar") -> Dict[str, str]:
    """Get prompts for specified language"""
    if language == "en":
        return PROMPTS_EN
    return PROMPTS_AR


def get_department_config(department: str) -> Dict:
    """Get configuration for a department"""
    return DEPARTMENTS_CONFIG.get(department, {})


def get_rule(rule_path: str, default=None):
    """
    Get a rule value using dot notation
    Example: get_rule("reception_rules.require_name")
    """
    parts = rule_path.split(".")
    current = CALL_CENTER_RULES

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default

    return current


def is_call_center_enabled() -> bool:
    """Check if call center mode is enabled"""
    return CALL_CENTER_ENABLED


def should_override_avatary(feature: str) -> bool:
    """Check if a specific avatary feature should be overridden"""
    return AVATARY_OVERRIDES.get(f"disable_{feature}", False)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "CALL_CENTER_MODE",
    "COMPANY_NAME",
    "BUSINESS_HOURS_START",
    "BUSINESS_HOURS_END",
    "DEPARTMENTS_CONFIG",
    "CALL_CENTER_RULES",
    "AVATARY_OVERRIDES",
    "PROMPTS_AR",
    "PROMPTS_EN",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "DB_TABLES",
    "FEATURES",
    "TTS_MODEL",
    "TTS_VOICE_DEFAULT",
    "TTS_VOICE_MAP",
    "AUDIO_OUTPUT_FORMAT",
    "AUDIO_OUTPUT_SAMPLE_RATE",
    "FALLBACK_TTS_ENABLED",
    "FALLBACK_TTS_SERVICE",
    "VAD_ENABLED",
    "VAD_THRESHOLD",
    "get_prompts",
    "get_department_config",
    "get_rule",
    "is_call_center_enabled",
    "should_override_avatary",
]
