#!/usr/bin/env python3
"""
Rules Engine for Call Center
Evaluates conditions and determines behavior based on rules
Overrides avatary agent behavior when in call center mode
"""

import logging
from typing import Dict, Any, Optional, List

# Use absolute imports - Docker runs with all files in /app
from config import (
    CALL_CENTER_RULES,
    AVATARY_OVERRIDES,
    get_rule,
    CALL_CENTER_ENABLED,
)
from models import (
    Department,
    TicketPriority,
    IVRStage,
    RoutingDecision,
)

logger = logging.getLogger(__name__)


# ============================================================================
# RULES ENGINE CLASS
# ============================================================================

class RulesEngine:
    """
    Evaluates call center rules and determines behavior
    Main purpose: Override avatary behavior based on call center context
    """

    def __init__(self):
        self.rules = CALL_CENTER_RULES
        self.overrides = AVATARY_OVERRIDES
        self.enabled = CALL_CENTER_ENABLED

    # ========================================================================
    # RECEPTION STAGE RULES
    # ========================================================================

    def should_require_field(self, field: str) -> bool:
        """Check if a field is required during reception"""
        field_name = f"require_{field}"
        return get_rule(f"reception_rules.{field_name}", False)

    def get_required_fields(self) -> List[str]:
        """Get list of required fields for reception"""
        required = []
        for field in ["name", "phone", "email", "service_type"]:
            if self.should_require_field(field):
                required.append(field)
        return required

    def validate_field(self, field: str, value: str) -> Dict[str, Any]:
        """
        Validate a field value against reception rules
        Returns: {"valid": bool, "error": Optional[str], "cleaned": Optional[str]}
        """
        rules = get_rule("reception_rules", {})

        # Name validation
        if field == "name":
            min_length = rules.get("name_min_length", 2)
            if len(value.strip()) < min_length:
                return {
                    "valid": False,
                    "error": f"Name must be at least {min_length} characters",
                }
            return {"valid": True, "cleaned": value.strip()}

        # Phone validation
        if field == "phone":
            min_length = rules.get("phone_min_length", 8)
            cleaned = "".join(filter(str.isdigit, value))
            if len(cleaned) < min_length:
                return {
                    "valid": False,
                    "error": f"Phone must be at least {min_length} digits",
                }
            return {"valid": True, "cleaned": cleaned}

        # Email validation
        if field == "email":
            if rules.get("email_validation", False):
                if "@" not in value or "." not in value:
                    return {"valid": False, "error": "Invalid email format"}
            return {"valid": True, "cleaned": value.strip()}

        # Service type validation
        if field == "service_type":
            if len(value.strip()) < 1:
                return {"valid": False, "error": "Service type is required"}
            return {"valid": True, "cleaned": value.strip()}

        return {"valid": True, "cleaned": value.strip()}

    def should_require_data_confirmation(self) -> bool:
        """Check if collected data should be confirmed with customer"""
        return get_rule("reception_rules.require_data_confirmation", False)

    def get_confirmation_retries(self) -> int:
        """Get number of confirmation retries allowed"""
        return get_rule("reception_rules.confirmation_retries", 1)

    # ========================================================================
    # ROUTING RULES
    # ========================================================================

    def route_to_department(
        self, service_type: str, collected_data: Optional[Dict] = None
    ) -> RoutingDecision:
        """
        Determine which department to route call to
        Returns: RoutingDecision with department and confidence
        """
        service_type_lower = service_type.lower() if service_type else ""

        # Get routing keywords from rules
        sales_keywords = get_rule(
            "reception_rules.auto_route_to_sales_keywords", []
        )
        complaints_keywords = get_rule(
            "reception_rules.auto_route_to_complaints_keywords", []
        )

        # Check for sales keywords
        sales_match_count = sum(
            1 for keyword in sales_keywords if keyword in service_type_lower
        )

        # Check for complaints keywords
        complaints_match_count = sum(
            1 for keyword in complaints_keywords if keyword in service_type_lower
        )

        # Determine primary department
        if complaints_match_count > sales_match_count:
            return RoutingDecision(
                department=Department.COMPLAINTS,
                reason=f"Matched {complaints_match_count} complaint keywords",
                confidence=min(0.95, 0.6 + complaints_match_count * 0.15),
                alternative_departments=[Department.RECEPTION],
            )

        if sales_match_count > 0:
            return RoutingDecision(
                department=Department.SALES,
                reason=f"Matched {sales_match_count} sales keywords",
                confidence=min(0.95, 0.6 + sales_match_count * 0.15),
                alternative_departments=[Department.RECEPTION],
            )

        # Default to reception if uncertain
        return RoutingDecision(
            department=Department.RECEPTION,
            reason="No clear department keywords matched. Defaulting to reception.",
            confidence=0.5,
            alternative_departments=[Department.SALES, Department.COMPLAINTS],
        )

    # ========================================================================
    # SALES RULES
    # ========================================================================

    def should_bot_handle_inquiry(self, inquiry: str) -> bool:
        """Check if bot should handle this inquiry or transfer to agent"""
        inquiry_lower = inquiry.lower() if inquiry else ""

        simple_keywords = get_rule("sales_rules.simple_inquiry_keywords", [])
        keyword_match = any(kw in inquiry_lower for kw in simple_keywords)

        if keyword_match and get_rule("sales_rules.bot_handles_simple_inquiries", False):
            return True

        return False

    def should_transfer_to_sales_agent(self, inquiry: str) -> bool:
        """Check if inquiry should be transferred to a sales agent"""
        inquiry_lower = inquiry.lower() if inquiry else ""

        transfer_keywords = get_rule("sales_rules.transfer_keywords", [])
        keyword_match = any(kw in inquiry_lower for kw in transfer_keywords)

        if keyword_match and get_rule("sales_rules.transfer_on_complex_inquiry", False):
            return True

        return False

    def should_enable_faq_responses(self) -> bool:
        """Check if FAQ responses should be enabled for sales"""
        return get_rule("sales_rules.enable_faq_responses", False)

    # ========================================================================
    # COMPLAINTS RULES
    # ========================================================================

    def should_auto_create_ticket(self) -> bool:
        """Check if ticket should be auto-created for complaints"""
        return get_rule("complaints_rules.auto_create_ticket", False)

    def determine_ticket_priority(self, complaint_text: str) -> TicketPriority:
        """Determine ticket priority based on complaint content"""
        complaint_lower = complaint_text.lower() if complaint_text else ""

        urgent_keywords = get_rule("complaints_rules.ticket_priority_urgent_keywords", [])
        if any(kw in complaint_lower for kw in urgent_keywords):
            return TicketPriority.URGENT

        return TicketPriority.MEDIUM

    def should_auto_transfer_complaint(self) -> bool:
        """Check if complex complaints should be auto-transferred to agent"""
        return get_rule("complaints_rules.auto_transfer_complex_complaints", False)

    def should_show_agent_customer_info(self) -> bool:
        """Check if agent should always see customer info before responding"""
        return get_rule("complaints_rules.always_show_agent_customer_info", False)

    # ========================================================================
    # GENERAL RULES
    # ========================================================================

    def get_default_language(self) -> str:
        """Get default language for interactions"""
        return get_rule("general_rules.default_language", "ar")

    def get_fallback_language(self) -> str:
        """Get fallback language if primary not available"""
        return get_rule("general_rules.fallback_language", "en")

    def should_auto_detect_language(self) -> bool:
        """Check if language should be auto-detected"""
        return get_rule("general_rules.auto_detect_language", True)

    def should_save_transcript(self) -> bool:
        """Check if transcript should be saved"""
        return get_rule("general_rules.save_transcript", True)

    def get_transcript_format(self) -> str:
        """Get transcript format (text only, no audio)"""
        return get_rule("general_rules.transcript_format", "text")

    def get_call_timeout_minutes(self) -> int:
        """Get call timeout in minutes"""
        return get_rule("general_rules.call_timeout_minutes", 30)

    def get_inactivity_timeout_minutes(self) -> int:
        """Get inactivity timeout in minutes"""
        return get_rule("general_rules.inactivity_timeout_minutes", 5)

    def get_max_queue_size(self) -> int:
        """Get maximum queue size"""
        return get_rule("general_rules.max_queue_size", 100)

    def get_max_wait_time_minutes(self) -> int:
        """Get maximum wait time in minutes"""
        return get_rule("general_rules.max_wait_time_minutes", 10)

    # ========================================================================
    # AVATARY OVERRIDE RULES
    # ========================================================================

    def should_disable_feature(self, feature: str) -> bool:
        """
        Check if an avatary feature should be disabled
        Features: avatar_display, face_recognition, visual_context, etc.
        """
        override_key = f"disable_{feature}"
        return self.overrides.get(override_key, False)

    def should_use_call_center_mode(self) -> bool:
        """Check if full call center mode should be used"""
        return self.overrides.get("use_call_center_prompts", False) and self.enabled

    def should_use_ivr_flow(self) -> bool:
        """Check if IVR flow should be used"""
        return self.overrides.get("use_ivr_flow", False) and self.enabled

    def should_collect_structured_data(self) -> bool:
        """Check if structured data collection should be used"""
        return self.overrides.get("collect_structured_data", False)

    def should_log_to_call_center_db(self) -> bool:
        """Check if calls should be logged to call center database"""
        return self.overrides.get("log_to_call_center_db", False)

    def should_create_tickets_from_complaints(self) -> bool:
        """Check if tickets should be auto-created from complaints"""
        return self.overrides.get("create_tickets_on_complaints", False)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def evaluate_condition(
        self, condition: str, context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition in given context
        Example condition: "service_type contains 'complaint'"
        """
        try:
            # Simple condition evaluation - can be extended
            # For now, check simple patterns
            if " contains " in condition:
                var, value = condition.split(" contains ")
                var = var.strip().strip("'\"")
                value = value.strip().strip("'\"")
                context_value = context.get(var, "")
                return value in str(context_value)

            return False
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def get_retention_policy(self) -> Dict[str, int]:
        """Get data retention policy (days)"""
        return {
            "transcripts": 90,
            "calls": 180,
            "tickets": 365,
            "customer_data": 730,  # 2 years
        }

    def log_rule_evaluation(
        self, rule_name: str, result: bool, context: Optional[Dict] = None
    ):
        """Log rule evaluation for audit trail"""
        logger.debug(f"Rule '{rule_name}' evaluated to {result}")
        if context:
            logger.debug(f"Context: {context}")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Create global rules engine instance
rules_engine = RulesEngine()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_rules_engine() -> RulesEngine:
    """Get or create rules engine instance"""
    return rules_engine


def is_call_center_enabled() -> bool:
    """Check if call center is enabled"""
    return rules_engine.enabled


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "RulesEngine",
    "get_rules_engine",
    "is_call_center_enabled",
    "rules_engine",
]
