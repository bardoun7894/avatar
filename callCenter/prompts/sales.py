#!/usr/bin/env python3
"""
Sales Department Prompts
Bilingual prompts for the sales/inquiry handling stage
"""

# ============================================================================
# ARABIC PROMPTS
# ============================================================================

SALES_PROMPTS_AR = {
    # Greeting
    "greeting": "أهلاً بك في قسم المبيعات. كيف يمكننا مساعدتك اليوم؟",
    "welcome_back": "مرحباً بعودتك {name}. ماذا تحتاج منا؟",

    # Data collection
    "ask_service_details": "هل يمكنك إخبارنا بالخدمة أو المنتج الذي تهتم به؟",
    "ask_budget": "ما هي الميزانية المتوقعة لهذا الطلب؟",
    "ask_timeline": "متى تحتاج هذه الخدمة؟",

    # FAQ answers
    "faq_products": "نحن نقدم مجموعة واسعة من المنتجات بما فيها...",
    "faq_pricing": "تتراوح أسعارنا من {min_price} إلى {max_price} حسب الخدمة.",
    "faq_payment_methods": "نقبل جميع طرق الدفع الآمنة بما فيها: بطاقات الائتمان، التحويلات البنكية، وغيرها.",
    "faq_delivery": "يتم التسليم عادة خلال {days} أيام عمل.",
    "faq_offers": "لدينا عروض خاصة هذا الشهر توفر {discount}% على المنتجات المختارة.",

    # Bot responses
    "offer_special": "عندنا عرض خاص لك اليوم! احصل على {discount}% خصم على طلبك الأول.",
    "request_demo": "هل تريد نموذج توضيحي للمنتج؟",
    "suggest_service": "بناءً على احتياجاتك، أقترح عليك الخدمة: {service_name}",

    # Complex inquiry handling
    "transfer_to_agent": "يبدو أن طلبك معقد ويحتاج اهتماماً خاصاً. سأوصلك بمتخصص لدينا.",
    "transfer_message": "شكراً لانتظارك. سيتحدث معك أحد متخصصي المبيعات الآن.",

    # Confirmation
    "confirm_interest": "هل أنت مهتم بـ {service_name}؟",
    "confirm_quote": "هل تريد عرض سعر من قسم المبيعات؟",

    # General messages
    "thank_you_for_interest": "شكراً لاهتمامك بخدماتنا.",
    "help_further": "هل هناك شيء آخر يمكننا مساعدتك به؟",
    "follow_up": "سيتم التواصل معك قريباً بتفاصيل العرض.",
}


# ============================================================================
# ENGLISH PROMPTS
# ============================================================================

SALES_PROMPTS_EN = {
    # Greeting
    "greeting": "Welcome to our Sales department. How can we help you today?",
    "welcome_back": "Welcome back, {name}. What can we do for you?",

    # Data collection
    "ask_service_details": "Could you tell us which service or product you're interested in?",
    "ask_budget": "What is your expected budget for this request?",
    "ask_timeline": "When do you need this service?",

    # FAQ answers
    "faq_products": "We offer a wide range of products including...",
    "faq_pricing": "Our prices range from {min_price} to {max_price} depending on the service.",
    "faq_payment_methods": "We accept all secure payment methods including: Credit cards, Bank transfers, and more.",
    "faq_delivery": "Delivery is typically within {days} business days.",
    "faq_offers": "We have special offers this month with {discount}% off on selected products.",

    # Bot responses
    "offer_special": "We have a special offer for you today! Get {discount}% discount on your first order.",
    "request_demo": "Would you like a demonstration of the product?",
    "suggest_service": "Based on your needs, I suggest our {service_name} service.",

    # Complex inquiry handling
    "transfer_to_agent": "It seems your request is complex and needs special attention. Let me connect you with a specialist.",
    "transfer_message": "Thank you for waiting. A sales specialist will speak with you now.",

    # Confirmation
    "confirm_interest": "Are you interested in {service_name}?",
    "confirm_quote": "Would you like a quote from our sales team?",

    # General messages
    "thank_you_for_interest": "Thank you for your interest in our services.",
    "help_further": "Is there anything else we can help you with?",
    "follow_up": "We will contact you soon with the details of the offer.",
}


# ============================================================================
# COMMON FAQ KNOWLEDGE BASE
# ============================================================================

SALES_FAQ = {
    "ar": {
        "products": [
            {"keyword": "منتج", "answer": "نحن نقدم عدة منتجات وخدمات متميزة..."},
            {"keyword": "خدمة", "answer": "خدماتنا مصممة لتلبية احتياجاتك..."},
        ],
        "pricing": [
            {"keyword": "سعر", "answer": "أسعارنا تنافسية وشفافة..."},
            {"keyword": "تكلفة", "answer": "التكلفة تختلف حسب نوع الخدمة..."},
        ],
        "offers": [
            {"keyword": "عرض", "answer": "لدينا عروض حصرية الآن..."},
            {"keyword": "خصم", "answer": "احصل على خصومات خاصة على طلباتك..."},
        ],
    },
    "en": {
        "products": [
            {"keyword": "product", "answer": "We offer several outstanding products and services..."},
            {"keyword": "service", "answer": "Our services are designed to meet your needs..."},
        ],
        "pricing": [
            {"keyword": "price", "answer": "Our prices are competitive and transparent..."},
            {"keyword": "cost", "answer": "Cost varies depending on the type of service..."},
        ],
        "offers": [
            {"keyword": "offer", "answer": "We have exclusive offers right now..."},
            {"keyword": "discount", "answer": "Get special discounts on your orders..."},
        ],
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sales_prompt(key: str, language: str = "ar", **kwargs) -> str:
    """
    Get a sales prompt in specified language
    Supports template substitution with kwargs

    Example:
        get_sales_prompt("faq_pricing", language="ar", min_price="100", max_price="1000")
    """
    prompts = SALES_PROMPTS_AR if language == "ar" else SALES_PROMPTS_EN

    prompt = prompts.get(key, "")

    if kwargs:
        try:
            prompt = prompt.format(**kwargs)
        except KeyError as e:
            print(f"Warning: Missing template variable {e}")

    return prompt


def get_all_sales_prompts(language: str = "ar") -> dict:
    """Get all sales prompts for a language"""
    return SALES_PROMPTS_AR if language == "ar" else SALES_PROMPTS_EN


def search_faq(query: str, language: str = "ar") -> str:
    """
    Search FAQ for a matching answer
    Returns relevant FAQ answer based on keywords
    """
    query_lower = query.lower()
    faq_lang = SALES_FAQ.get(language, SALES_FAQ.get("en"))

    # Search through all categories
    for category, items in faq_lang.items():
        for item in items:
            if item["keyword"] in query_lower:
                return item["answer"]

    return ""


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "SALES_PROMPTS_AR",
    "SALES_PROMPTS_EN",
    "SALES_FAQ",
    "get_sales_prompt",
    "get_all_sales_prompts",
    "search_faq",
]
