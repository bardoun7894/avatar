#!/usr/bin/env python3
"""
Reception Department Prompts
Bilingual prompts for the reception/initial contact stage
"""

# ============================================================================
# ARABIC PROMPTS
# ============================================================================

RECEPTION_PROMPTS_AR = {
    # Greeting and welcome
    "greeting": "أهلاً وسهلاً بكم. نحن هنا لمساعدتك بأفضل طريقة. سنقوم بجمع بعض المعلومات البسيطة لتقديم خدمة أفضل.",
    "greeting_repeat": "شكراً على انتظارك. سنستمر في جمع معلوماتك.",

    # Data collection
    "ask_name": "من فضلك، ما اسمك الكامل؟",
    "ask_name_again": "عذراً، هل يمكنك تكرار اسمك من فضلك؟",
    "ask_phone": "يرجى إدخال أو نطق رقم هاتفك.",
    "ask_phone_again": "عذراً، هل يمكنك تكرار رقم هاتفك؟",
    "ask_email": "ما هو بريدك الإلكتروني؟",
    "ask_email_again": "عذراً، هل يمكنك تكرار بريدك الإلكتروني؟",
    "ask_service_type": "ما نوع الخدمة أو المنتج الذي تحتاج إليه؟",
    "ask_service_type_again": "هل يمكنك إعادة صياغة طلبك؟",

    # Validation messages
    "invalid_name": "عذراً، لم أفهم الاسم. يرجى المحاولة مرة أخرى بشكل واضح.",
    "invalid_phone": "عذراً، رقم الهاتف غير صحيح. يرجى إدخال رقم صحيح.",
    "invalid_email": "عذراً، البريد الإلكتروني غير صحيح. يرجى المحاولة مرة أخرى.",
    "invalid_service": "عذراً، لم أفهم نوع الخدمة المطلوبة. يرجى تحديد واحدة من: بيع، شكوى، أو استفسار.",

    # Confirmation
    "confirm_data": (
        "دعني أتأكد من البيانات التالية:\n"
        "الاسم: {name}\n"
        "الهاتف: {phone}\n"
        "البريد: {email}\n"
        "نوع الخدمة: {service_type}\n"
        "هل هذه البيانات صحيحة؟ قل 'نعم' أو اضغط 1 للتأكيد، أو قل 'لا' أو اضغط 2 للتعديل."
    ),

    # Retry and escalation
    "retry_message": "يرجى المحاولة مرة أخرى.",
    "max_retries_reached": (
        "عذراً، واجهنا صعوبة في جمع البيانات. "
        "سيتم نقل مكالمتك إلى ممثل العملاء الذي سيساعدك بشكل أفضل."
    ),

    # Routing messages
    "routing_to_sales": "شكراً على معلوماتك. سيتم توجيهك إلى قسم المبيعات. يرجى الانتظار قليلاً.",
    "routing_to_complaints": "شكراً على معلوماتك. سيتم توجيهك إلى قسم معالجة الشكاوى. يرجى الانتظار قليلاً.",
    "hold_music_message": "شكراً على انتظارك. سيكون متاح معك ممثل قريباً.",

    # Frequently asked questions
    "business_hours": "ساعات عملنا من التاسعة صباحاً إلى السادسة مساءً من يوم السبت إلى الخميس.",
    "company_location": "تقع شركتنا في {location}.",
    "support_number": "يمكنك أيضاً الاتصال بنا مباشرة على الرقم {phone_number}.",

    # General messages
    "listening": "أنا أستمع إليك...",
    "processing": "دعني أعالج طلبك...",
    "thank_you": "شكراً لك. نقدر وقتك.",
}


# ============================================================================
# ENGLISH PROMPTS
# ============================================================================

RECEPTION_PROMPTS_EN = {
    # Greeting and welcome
    "greeting": "Welcome! We're here to help you. Let's collect some information to serve you better.",
    "greeting_repeat": "Thank you for waiting. Let's continue collecting your information.",

    # Data collection
    "ask_name": "Please tell me your full name.",
    "ask_name_again": "Sorry, could you please repeat your name?",
    "ask_phone": "Please enter or say your phone number.",
    "ask_phone_again": "Sorry, could you please repeat your phone number?",
    "ask_email": "What is your email address?",
    "ask_email_again": "Sorry, could you please repeat your email address?",
    "ask_service_type": "What type of service or product are you interested in?",
    "ask_service_type_again": "Could you please clarify what you need?",

    # Validation messages
    "invalid_name": "Sorry, I didn't understand the name. Please try again clearly.",
    "invalid_phone": "Sorry, the phone number is invalid. Please enter a correct number.",
    "invalid_email": "Sorry, the email address is invalid. Please try again.",
    "invalid_service": "Sorry, I didn't understand the service type. Please choose: Sales, Complaints, or Inquiry.",

    # Confirmation
    "confirm_data": (
        "Let me confirm your information:\n"
        "Name: {name}\n"
        "Phone: {phone}\n"
        "Email: {email}\n"
        "Service Type: {service_type}\n"
        "Is this correct? Say 'yes' or press 1 to confirm, or say 'no' or press 2 to edit."
    ),

    # Retry and escalation
    "retry_message": "Please try again.",
    "max_retries_reached": (
        "Sorry, we had difficulty collecting your information. "
        "You will now be connected to a customer representative who can help you better."
    ),

    # Routing messages
    "routing_to_sales": "Thank you for your information. You will be routed to the Sales department. Please wait.",
    "routing_to_complaints": "Thank you for your information. You will be routed to the Complaints department. Please wait.",
    "hold_music_message": "Thank you for waiting. An agent will be available with you shortly.",

    # Frequently asked questions
    "business_hours": "Our business hours are 9 AM to 6 PM, Saturday through Thursday.",
    "company_location": "Our office is located at {location}.",
    "support_number": "You can also reach us directly at {phone_number}.",

    # General messages
    "listening": "I'm listening...",
    "processing": "Let me process your request...",
    "thank_you": "Thank you. We appreciate your time.",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_reception_prompt(key: str, language: str = "ar", **kwargs) -> str:
    """
    Get a reception prompt in specified language
    Supports template substitution with kwargs

    Example:
        get_reception_prompt("confirm_data", language="ar", name="أحمد", phone="123456")
    """
    prompts = RECEPTION_PROMPTS_AR if language == "ar" else RECEPTION_PROMPTS_EN

    prompt = prompts.get(key, "")

    if kwargs:
        try:
            prompt = prompt.format(**kwargs)
        except KeyError as e:
            print(f"Warning: Missing template variable {e}")

    return prompt


def get_all_reception_prompts(language: str = "ar") -> dict:
    """Get all reception prompts for a language"""
    return RECEPTION_PROMPTS_AR if language == "ar" else RECEPTION_PROMPTS_EN


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "RECEPTION_PROMPTS_AR",
    "RECEPTION_PROMPTS_EN",
    "get_reception_prompt",
    "get_all_reception_prompts",
]
