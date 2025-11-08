#!/usr/bin/env python3
"""
Call Center Department-Specific Prompts
Bilingual (Arabic/English) prompts for all departments
"""

from .reception import (
    RECEPTION_PROMPTS_AR,
    RECEPTION_PROMPTS_EN,
    get_reception_prompt,
    get_all_reception_prompts,
)
from .sales import (
    SALES_PROMPTS_AR,
    SALES_PROMPTS_EN,
    SALES_FAQ,
    get_sales_prompt,
    get_all_sales_prompts,
    search_faq,
)
from .complaints import (
    COMPLAINTS_PROMPTS_AR,
    COMPLAINTS_PROMPTS_EN,
    SEVERITY_LEVELS,
    COMPLAINT_CATEGORIES,
    get_complaints_prompt,
    get_all_complaints_prompts,
    get_complaint_categories,
    determine_severity,
)

__all__ = [
    # Reception
    "RECEPTION_PROMPTS_AR",
    "RECEPTION_PROMPTS_EN",
    "get_reception_prompt",
    "get_all_reception_prompts",

    # Sales
    "SALES_PROMPTS_AR",
    "SALES_PROMPTS_EN",
    "SALES_FAQ",
    "get_sales_prompt",
    "get_all_sales_prompts",
    "search_faq",

    # Complaints
    "COMPLAINTS_PROMPTS_AR",
    "COMPLAINTS_PROMPTS_EN",
    "SEVERITY_LEVELS",
    "COMPLAINT_CATEGORIES",
    "get_complaints_prompt",
    "get_all_complaints_prompts",
    "get_complaint_categories",
    "determine_severity",
]
