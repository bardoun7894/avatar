#!/usr/bin/env python3
"""
Complaints Department Prompts
Bilingual prompts for the complaints/support handling stage
"""

# ============================================================================
# ARABIC PROMPTS
# ============================================================================

COMPLAINTS_PROMPTS_AR = {
    # Greeting
    "greeting": "أهلاً بك في قسم معالجة الشكاوى. نحن هنا لحل مشكلتك. يرجى شرح المشكلة.",
    "welcome_back": "مرحباً بعودتك {name}. كيف يمكننا مساعدتك؟",
    "empathy": "أفهم أن هذا الموقف محبط. دعني أساعدك في حل هذه المشكلة.",

    # Data collection
    "ask_complaint_type": "ما نوع الشكوى التي لديك؟",
    "ask_complaint_details": "يرجى شرح المشكلة بالتفصيل. ماذا حدث بالضبط؟",
    "ask_when_occurred": "متى حدثت هذه المشكلة؟",
    "ask_previous_reports": "هل تم الإبلاغ عن هذه المشكلة من قبل؟",

    # Complaint types
    "complaint_type_quality": "مشكلة في جودة الخدمة/المنتج",
    "complaint_type_delivery": "مشكلة في التسليم",
    "complaint_type_billing": "مشكلة في الفواتير والدفع",
    "complaint_type_support": "مشكلة في الدعم الفني",
    "complaint_type_general": "شكوى عامة",

    # Ticket creation
    "ticket_created": "تم إنشاء تذكرة برقم {ticket_id} لمتابعة شكواك.",
    "ticket_assignment": "سيتم تعيين متخصص لمراجعة شكواك بسرعة.",

    # Severity assessment
    "is_urgent": "هل هذه المشكلة عاجلة أم طارئة؟",
    "urgent_handling": "سيتم توجيه شكواك العاجلة مباشرة لمتخصص لدينا.",
    "normal_handling": "سيتم معالجة شكواك في الوقت المحدد.",

    # Agent transfer
    "transfer_to_agent": "سأوصلك الآن بأحد متخصصي قسم الشكاوى الذي سيتعامل مع حالتك بشكل مباشر.",
    "agent_available_soon": "سيكون متاح معك متخصص قريباً جداً.",

    # Resolution options
    "apology": "نعتذر عما حدث. نقدر تقدمك بالشكوى.",
    "offer_solution": "ما الحل الذي تتوقع أن يحل المشكلة؟",
    "compensation": "قد نوفر لك بدلاً أو تعويضاً عن الإزعاج الذي سببناه.",

    # Follow-up
    "follow_up_timeline": "سنتواصل معك خلال {hours} ساعة بتحديث عن الشكوى.",
    "expected_resolution": "ننتظر حل المشكلة خلال {days} أيام.",
    "contact_for_updates": "يمكنك التواصل معنا برقم التذكرة {ticket_id} للاستفسار عن التقدم.",

    # General messages
    "thank_you_for_feedback": "شكراً لك على ملاحظاتك. هذا يساعدنا على التحسن.",
    "help_further": "هل هناك شيء آخر نستطيع مساعدتك به؟",
    "apologies_again": "نعتذر مجدداً عن هذا الموقف غير المقبول.",
}


# ============================================================================
# ENGLISH PROMPTS
# ============================================================================

COMPLAINTS_PROMPTS_EN = {
    # Greeting
    "greeting": "Welcome to our Complaints department. We're here to resolve your issue. Please describe the problem.",
    "welcome_back": "Welcome back, {name}. How can we help you?",
    "empathy": "I understand this situation is frustrating. Let me help you resolve this issue.",

    # Data collection
    "ask_complaint_type": "What type of complaint do you have?",
    "ask_complaint_details": "Please describe the issue in detail. What exactly happened?",
    "ask_when_occurred": "When did this problem occur?",
    "ask_previous_reports": "Has this issue been reported before?",

    # Complaint types
    "complaint_type_quality": "Quality of Service/Product Issue",
    "complaint_type_delivery": "Delivery Problem",
    "complaint_type_billing": "Billing and Payment Issue",
    "complaint_type_support": "Technical Support Issue",
    "complaint_type_general": "General Complaint",

    # Ticket creation
    "ticket_created": "A ticket has been created with number {ticket_id} to track your complaint.",
    "ticket_assignment": "A specialist will review your complaint shortly.",

    # Severity assessment
    "is_urgent": "Is this issue urgent or critical?",
    "urgent_handling": "Your urgent complaint will be directed directly to a specialist.",
    "normal_handling": "Your complaint will be handled within the normal timeframe.",

    # Agent transfer
    "transfer_to_agent": "I'm connecting you now with a complaints specialist who will handle your case directly.",
    "agent_available_soon": "A specialist will be available with you very soon.",

    # Resolution options
    "apology": "We apologize for what happened. We appreciate you reporting this issue.",
    "offer_solution": "What solution do you think would resolve this issue?",
    "compensation": "We may provide you with a refund or compensation for the inconvenience.",

    # Follow-up
    "follow_up_timeline": "We will contact you within {hours} hours with an update on your complaint.",
    "expected_resolution": "We expect to resolve the issue within {days} days.",
    "contact_for_updates": "You can contact us using ticket number {ticket_id} for updates on the progress.",

    # General messages
    "thank_you_for_feedback": "Thank you for your feedback. It helps us improve.",
    "help_further": "Is there anything else we can help you with?",
    "apologies_again": "We apologize again for this unacceptable situation.",
}


# ============================================================================
# COMPLAINT SEVERITY LEVELS
# ============================================================================

SEVERITY_LEVELS = {
    "critical": {
        "ar": "حرج - يتطلب تدخل فوري",
        "en": "Critical - Requires immediate intervention",
        "priority": "urgent",
        "max_resolution_hours": 4,
    },
    "high": {
        "ar": "عالي - يتطلب متابعة سريعة",
        "en": "High - Requires quick follow-up",
        "priority": "high",
        "max_resolution_hours": 24,
    },
    "medium": {
        "ar": "متوسط - معالجة عادية",
        "en": "Medium - Normal handling",
        "priority": "medium",
        "max_resolution_hours": 72,
    },
    "low": {
        "ar": "منخفض - معلومة أو استفسار",
        "en": "Low - Information or inquiry",
        "priority": "low",
        "max_resolution_hours": 120,
    },
}


# ============================================================================
# COMPLAINT CATEGORIES
# ============================================================================

COMPLAINT_CATEGORIES = {
    "ar": [
        {"key": "quality", "label": "جودة الخدمة/المنتج"},
        {"key": "delivery", "label": "التسليم والتوصيل"},
        {"key": "billing", "label": "الفواتير والدفع"},
        {"key": "support", "label": "الدعم الفني"},
        {"key": "behavior", "label": "السلوك والتعامل"},
        {"key": "general", "label": "شكوى عامة"},
    ],
    "en": [
        {"key": "quality", "label": "Quality of Service/Product"},
        {"key": "delivery", "label": "Delivery and Shipping"},
        {"key": "billing", "label": "Billing and Payment"},
        {"key": "support", "label": "Technical Support"},
        {"key": "behavior", "label": "Behavior and Treatment"},
        {"key": "general", "label": "General Complaint"},
    ],
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_complaints_prompt(key: str, language: str = "ar", **kwargs) -> str:
    """
    Get a complaints prompt in specified language
    Supports template substitution with kwargs

    Example:
        get_complaints_prompt("ticket_created", language="ar", ticket_id="TKT12345")
    """
    prompts = COMPLAINTS_PROMPTS_AR if language == "ar" else COMPLAINTS_PROMPTS_EN

    prompt = prompts.get(key, "")

    if kwargs:
        try:
            prompt = prompt.format(**kwargs)
        except KeyError as e:
            print(f"Warning: Missing template variable {e}")

    return prompt


def get_all_complaints_prompts(language: str = "ar") -> dict:
    """Get all complaints prompts for a language"""
    return COMPLAINTS_PROMPTS_AR if language == "ar" else COMPLAINTS_PROMPTS_EN


def get_complaint_categories(language: str = "ar") -> list:
    """Get complaint categories for a language"""
    return COMPLAINT_CATEGORIES.get(language, COMPLAINT_CATEGORIES["en"])


def determine_severity(complaint_keywords: str) -> str:
    """
    Determine severity level based on complaint keywords
    Returns: "critical", "high", "medium", or "low"
    """
    urgent_keywords = [
        "عاجل", "حرج", "طوارئ", "يموت", "خطير",
        "urgent", "critical", "emergency", "dying", "severe"
    ]
    high_keywords = [
        "مهم", "سريع", "مشكلة", "خسارة",
        "important", "quick", "issue", "loss"
    ]

    complaint_lower = complaint_keywords.lower() if complaint_keywords else ""

    if any(kw in complaint_lower for kw in urgent_keywords):
        return "critical"

    if any(kw in complaint_lower for kw in high_keywords):
        return "high"

    # Check for repeated patterns (multiple issues)
    if complaint_lower.count("و") > 2 or complaint_lower.count("and") > 2:
        return "medium"

    return "low"


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "COMPLAINTS_PROMPTS_AR",
    "COMPLAINTS_PROMPTS_EN",
    "SEVERITY_LEVELS",
    "COMPLAINT_CATEGORIES",
    "get_complaints_prompt",
    "get_all_complaints_prompts",
    "get_complaint_categories",
    "determine_severity",
]
