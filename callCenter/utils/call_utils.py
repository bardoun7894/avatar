#!/usr/bin/env python3
"""
Call Center Utility Functions
Common helper functions for call processing
"""

import re
import uuid
from datetime import datetime
from typing import Optional, Dict, Tuple
from ..models import CallDirection, Department


# ============================================================================
# PHONE NUMBER UTILITIES
# ============================================================================

def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to standard format
    Removes all non-digit characters
    """
    if not phone:
        return ""
    return "".join(filter(str.isdigit, phone))


def validate_phone(phone: str, min_length: int = 8) -> bool:
    """
    Validate phone number
    Returns True if phone is valid
    """
    normalized = normalize_phone(phone)
    return len(normalized) >= min_length


def format_phone_for_display(phone: str, format_type: str = "standard") -> str:
    """
    Format phone number for display
    format_type: "standard", "international", "local"
    """
    normalized = normalize_phone(phone)

    if format_type == "international" and len(normalized) == 10:
        return f"+966{normalized[1:]}"  # Saudi example
    elif format_type == "local":
        if normalized.startswith("0"):
            return normalized
        elif len(normalized) == 10:
            return f"0{normalized[1:]}"
        return normalized

    # Standard: add spacing
    if len(normalized) == 10:
        return f"{normalized[:3]}-{normalized[3:6]}-{normalized[6:]}"

    return normalized


# ============================================================================
# EMAIL UTILITIES
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def extract_email_domain(email: str) -> Optional[str]:
    """Extract domain from email"""
    if not email or "@" not in email:
        return None
    return email.split("@")[1]


# ============================================================================
# NAME UTILITIES
# ============================================================================

def normalize_name(name: str) -> str:
    """
    Normalize name (capitalize first letter of each word)
    """
    if not name:
        return ""
    return " ".join(word.capitalize() for word in name.strip().split())


def validate_name(name: str, min_length: int = 2) -> bool:
    """
    Validate name
    """
    if not name:
        return False
    return len(name.strip()) >= min_length


def is_arabic_name(name: str) -> bool:
    """Check if name contains Arabic characters"""
    if not name:
        return False
    return any('\u0600' <= char <= '\u06FF' for char in name)


# ============================================================================
# CALL ID UTILITIES
# ============================================================================

def generate_call_id(prefix: str = "CALL") -> str:
    """Generate unique call ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"{prefix}_{timestamp}_{unique_id}"


def generate_ticket_id(prefix: str = "TKT") -> str:
    """Generate unique ticket ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:4].upper()
    return f"{prefix}_{timestamp}_{unique_id}"


def generate_customer_id(prefix: str = "CUST") -> str:
    """Generate unique customer ID"""
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}_{unique_id}"


# ============================================================================
# DURATION UTILITIES
# ============================================================================

def calculate_duration(start_time: datetime, end_time: datetime) -> int:
    """Calculate duration in seconds between two times"""
    if not start_time or not end_time:
        return 0
    delta = end_time - start_time
    return int(delta.total_seconds())


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 0:
        return "0s"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

def detect_language(text: str) -> str:
    """
    Detect language from text
    Returns: "ar" for Arabic, "en" for English, or "mixed"
    """
    if not text:
        return "en"

    arabic_count = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    english_count = sum(1 for char in text if char.isalpha() and ord(char) < 128)

    total = arabic_count + english_count

    if total == 0:
        return "en"

    arabic_ratio = arabic_count / total

    if arabic_ratio > 0.7:
        return "ar"
    elif arabic_ratio > 0.3:
        return "mixed"
    else:
        return "en"


# ============================================================================
# TEXT EXTRACTION & PARSING
# ============================================================================

def extract_numbers(text: str) -> list:
    """Extract all numbers from text"""
    return re.findall(r'\d+', text)


def extract_urls(text: str) -> list:
    """Extract URLs from text"""
    pattern = r'https?://[^\s]+'
    return re.findall(pattern, text)


def clean_text(text: str) -> str:
    """
    Clean text (remove extra spaces, special chars)
    """
    if not text:
        return ""
    # Remove extra spaces
    text = " ".join(text.split())
    # Remove special unicode spaces
    text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    return text


# ============================================================================
# STATUS & DEPARTMENT UTILITIES
# ============================================================================

def get_department_name(department: Department, language: str = "ar") -> str:
    """Get department display name"""
    names = {
        Department.RECEPTION: {"ar": "الاستقبال", "en": "Reception"},
        Department.SALES: {"ar": "المبيعات", "en": "Sales"},
        Department.COMPLAINTS: {"ar": "الشكاوى", "en": "Complaints"},
    }

    if department in names:
        return names[department].get(language, names[department].get("en"))

    return str(department)


def get_direction_name(direction: CallDirection, language: str = "ar") -> str:
    """Get call direction display name"""
    names = {
        CallDirection.INBOUND: {"ar": "وارد", "en": "Inbound"},
        CallDirection.OUTBOUND: {"ar": "صادر", "en": "Outbound"},
    }

    if direction in names:
        return names[direction].get(language, names[direction].get("en"))

    return str(direction)


# ============================================================================
# SENTIMENT ANALYSIS HELPERS
# ============================================================================

def extract_sentiment_keywords(text: str, language: str = "ar") -> Dict[str, list]:
    """
    Extract sentiment indicators from text
    Returns positive, negative, and neutral keywords found
    """
    positive_ar = ["ممتاز", "رائع", "ممتازة", "شكراً", "شكر", "جزاك", "حلو"]
    negative_ar = ["سيء", "مشكلة", "خطأ", "لا", "غضب", "حزين", "ساخط"]

    positive_en = ["excellent", "great", "awesome", "thank", "perfect", "good"]
    negative_en = ["bad", "poor", "problem", "error", "angry", "sad", "upset"]

    text_lower = text.lower() if text else ""

    positive_found = []
    negative_found = []
    neutral_found = []

    keywords = positive_ar if language == "ar" else positive_en
    for kw in keywords:
        if kw in text_lower:
            positive_found.append(kw)

    keywords = negative_ar if language == "ar" else negative_en
    for kw in keywords:
        if kw in text_lower:
            negative_found.append(kw)

    return {
        "positive": positive_found,
        "negative": negative_found,
        "neutral": neutral_found,
    }


def calculate_sentiment(text: str, language: str = "ar") -> str:
    """
    Simple sentiment analysis
    Returns: "positive", "negative", or "neutral"
    """
    sentiments = extract_sentiment_keywords(text, language)

    positive_count = len(sentiments["positive"])
    negative_count = len(sentiments["negative"])

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    # Phone utilities
    "normalize_phone",
    "validate_phone",
    "format_phone_for_display",

    # Email utilities
    "validate_email",
    "extract_email_domain",

    # Name utilities
    "normalize_name",
    "validate_name",
    "is_arabic_name",

    # ID generation
    "generate_call_id",
    "generate_ticket_id",
    "generate_customer_id",

    # Duration
    "calculate_duration",
    "format_duration",

    # Language
    "detect_language",

    # Text utilities
    "extract_numbers",
    "extract_urls",
    "clean_text",

    # Status & department
    "get_department_name",
    "get_direction_name",

    # Sentiment
    "extract_sentiment_keywords",
    "calculate_sentiment",
]
