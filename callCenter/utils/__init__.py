#!/usr/bin/env python3
"""
Call Center Utilities
Helper functions and utilities for call processing
"""

from .call_utils import (
    normalize_phone,
    validate_phone,
    format_phone_for_display,
    validate_email,
    extract_email_domain,
    normalize_name,
    validate_name,
    is_arabic_name,
    generate_call_id,
    generate_ticket_id,
    generate_customer_id,
    calculate_duration,
    format_duration,
    detect_language,
    extract_numbers,
    extract_urls,
    clean_text,
    get_department_name,
    get_direction_name,
    extract_sentiment_keywords,
    calculate_sentiment,
)

__all__ = [
    "normalize_phone",
    "validate_phone",
    "format_phone_for_display",
    "validate_email",
    "extract_email_domain",
    "normalize_name",
    "validate_name",
    "is_arabic_name",
    "generate_call_id",
    "generate_ticket_id",
    "generate_customer_id",
    "calculate_duration",
    "format_duration",
    "detect_language",
    "extract_numbers",
    "extract_urls",
    "clean_text",
    "get_department_name",
    "get_direction_name",
    "extract_sentiment_keywords",
    "calculate_sentiment",
]
