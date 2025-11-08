#!/usr/bin/env python3
"""
Call Router - IVR and Smart Routing Logic
Handles the flow of calls through the IVR system and routes to appropriate departments
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .models import (
    IVRStage,
    Department,
    IVRStageResponse,
    RoutingDecision,
    Call,
)
from .rules_engine import get_rules_engine
from .config import get_prompts
from .prompts.routing_prompts import (
    ReceptionPrompts,
    SalesPrompts,
    ComplaintsPrompts,
    IntentDetectionRules,
    IntentDetection,
    RoutingDecision as IntentRoutingDecision,
    route_by_intent,
    CustomerInfo,
    IntentEnum,
    DepartmentEnum,
    RECEPTION_PERSONA,
    SALES_PERSONA,
    COMPLAINTS_PERSONA,
    DepartmentPersona,
)

logger = logging.getLogger(__name__)


# ============================================================================
# CALL ROUTER CLASS
# ============================================================================

class CallRouter:
    """
    Manages call flow through IVR and routes to departments
    Main responsibility: Guide call through reception stage and route to appropriate department
    """

    def __init__(self):
        self.rules_engine = get_rules_engine()

    # ========================================================================
    # WELCOME & GREETING
    # ========================================================================

    def get_welcome_stage(self, language: str = "ar") -> IVRStageResponse:
        """
        Initial welcome message for the call
        """
        prompts = get_prompts(language)

        return IVRStageResponse(
            current_stage=IVRStage.WELCOME,
            prompt=prompts.get("greeting", "Welcome"),
            language=language,
            expected_input="acknowledgment",
        )

    # ========================================================================
    # DATA COLLECTION STAGES
    # ========================================================================

    def get_name_collection_stage(self, language: str = "ar") -> IVRStageResponse:
        """
        Prompt for customer name
        """
        prompts = get_prompts(language)

        return IVRStageResponse(
            current_stage=IVRStage.COLLECT_NAME,
            prompt=prompts.get("ask_name", "Please provide your name"),
            language=language,
            expected_input="name",
        )

    def get_phone_collection_stage(self, language: str = "ar") -> IVRStageResponse:
        """
        Prompt for customer phone
        """
        prompts = get_prompts(language)

        return IVRStageResponse(
            current_stage=IVRStage.COLLECT_PHONE,
            prompt=prompts.get("ask_phone", "Please provide your phone number"),
            language=language,
            expected_input="phone",
        )

    def get_email_collection_stage(self, language: str = "ar") -> IVRStageResponse:
        """
        Prompt for customer email
        """
        prompts = get_prompts(language)

        return IVRStageResponse(
            current_stage=IVRStage.COLLECT_EMAIL,
            prompt=prompts.get("ask_email", "Please provide your email"),
            language=language,
            expected_input="email",
        )

    def get_service_type_collection_stage(
        self, language: str = "ar"
    ) -> IVRStageResponse:
        """
        Prompt for service type
        """
        prompts = get_prompts(language)

        return IVRStageResponse(
            current_stage=IVRStage.COLLECT_SERVICE_TYPE,
            prompt=prompts.get(
                "ask_service_type", "What type of service do you need?"
            ),
            language=language,
            expected_input="service_type",
        )

    # ========================================================================
    # DATA CONFIRMATION
    # ========================================================================

    def get_confirmation_stage(
        self, collected_data: Dict[str, Any], language: str = "ar"
    ) -> IVRStageResponse:
        """
        Generate confirmation message with collected data
        """
        prompts = get_prompts(language)

        confirmation_template = prompts.get(
            "confirm_data",
            "Please confirm: name {name}, phone {phone}, email {email}, service {service_type}",
        )

        confirmation_message = confirmation_template.format(
            name=collected_data.get("name", ""),
            phone=collected_data.get("phone", ""),
            email=collected_data.get("email", ""),
            service_type=collected_data.get("service_type", ""),
        )

        return IVRStageResponse(
            current_stage=IVRStage.CONFIRM_DATA,
            prompt=confirmation_message,
            language=language,
            expected_input="confirmation",
        )

    # ========================================================================
    # DEPARTMENT ROUTING
    # ========================================================================

    def get_next_stage(
        self, current_stage: IVRStage, collected_data: Optional[Dict] = None
    ) -> IVRStage:
        """
        Determine next IVR stage based on current stage
        """
        required_fields = self.rules_engine.get_required_fields()

        stage_flow = {
            IVRStage.WELCOME: IVRStage.COLLECT_NAME,
            IVRStage.COLLECT_NAME: (
                IVRStage.COLLECT_PHONE
                if "phone" in required_fields
                else IVRStage.COLLECT_EMAIL
            ),
            IVRStage.COLLECT_PHONE: (
                IVRStage.COLLECT_EMAIL
                if "email" in required_fields
                else IVRStage.COLLECT_SERVICE_TYPE
            ),
            IVRStage.COLLECT_EMAIL: (
                IVRStage.COLLECT_SERVICE_TYPE
                if "service_type" in required_fields
                else IVRStage.CONFIRM_DATA
            ),
            IVRStage.COLLECT_SERVICE_TYPE: IVRStage.CONFIRM_DATA,
            IVRStage.CONFIRM_DATA: IVRStage.ROUTE_TO_DEPARTMENT,
            IVRStage.ROUTE_TO_DEPARTMENT: IVRStage.DEPARTMENT_HANDLING,
            IVRStage.DEPARTMENT_HANDLING: IVRStage.CALL_ENDED,
            IVRStage.CALL_ENDED: IVRStage.CALL_ENDED,
        }

        return stage_flow.get(current_stage, IVRStage.DEPARTMENT_HANDLING)

    def route_call(self, service_type: str) -> RoutingDecision:
        """
        Route call to appropriate department based on service type
        """
        return self.rules_engine.route_to_department(service_type)

    def detect_intent_from_message(self, message: str, language: str = "ar") -> IntentEnum:
        """
        Detect customer intent from their message
        Uses keyword matching from routing_prompts
        """
        return IntentDetectionRules.detect_intent(message, language)

    def route_by_detected_intent(self, intent: IntentEnum) -> DepartmentEnum:
        """
        Route customer to appropriate department based on detected intent
        """
        return route_by_intent(intent)

    def get_intent_routing_decision(
        self,
        call_id: str,
        message: str,
        customer_info: Optional[CustomerInfo] = None,
        language: str = "ar"
    ) -> IntentRoutingDecision:
        """
        Create a complete routing decision based on intent detection
        Returns Pydantic model with all routing details
        """
        # Detect intent from message
        intent = self.detect_intent_from_message(message, language)

        # Determine target department
        department = self.route_by_detected_intent(intent)

        # Get keywords that triggered this intent
        keywords = []
        if intent == IntentEnum.COMPLAINT:
            keywords = IntentDetectionRules.COMPLAINT_KEYWORDS.get(language, [])
        elif intent == IntentEnum.SERVICE_INQUIRY:
            keywords = IntentDetectionRules.SERVICE_INQUIRY_KEYWORDS.get(language, [])
        elif intent == IntentEnum.TRAINING_INQUIRY:
            keywords = IntentDetectionRules.TRAINING_KEYWORDS.get(language, [])

        # Create intent detection result
        intent_detection = IntentDetection(
            intent=intent,
            department=department,
            confidence=0.95 if any(kw in message.lower() for kw in keywords) else 0.7,
            keywords=keywords,
            reasoning=f"Detected {intent.value} from customer message - routing to {department.value}"
        )

        # Create routing decision
        routing_decision = IntentRoutingDecision(
            call_id=call_id,
            customer_info=customer_info or CustomerInfo(),
            intent_detection=intent_detection,
            timestamp=datetime.now().isoformat()
        )

        return routing_decision

    def get_department_greeting(self, department: DepartmentEnum, language: str = "ar") -> str:
        """Get welcome message for specific department"""
        if department == DepartmentEnum.SALES:
            return SalesPrompts.get(language, "welcome")
        elif department == DepartmentEnum.COMPLAINTS:
            return ComplaintsPrompts.get(language, "welcome")
        else:
            return ReceptionPrompts.get(language, "greeting")

    def get_reception_prompt(self, prompt_key: str, language: str = "ar", **kwargs) -> str:
        """Get reception department prompt"""
        return ReceptionPrompts.get(language, prompt_key, **kwargs)

    def get_sales_prompt(self, prompt_key: str, language: str = "ar", **kwargs) -> str:
        """Get sales department prompt"""
        return SalesPrompts.get(language, prompt_key, **kwargs)

    def get_complaints_prompt(self, prompt_key: str, language: str = "ar", **kwargs) -> str:
        """Get complaints department prompt"""
        return ComplaintsPrompts.get(language, prompt_key, **kwargs)

    def get_department_persona(self, department: DepartmentEnum) -> DepartmentPersona:
        """Get persona (assistant details) for a specific department"""
        persona_map = {
            DepartmentEnum.RECEPTION: RECEPTION_PERSONA,
            DepartmentEnum.SALES: SALES_PERSONA,
            DepartmentEnum.COMPLAINTS: COMPLAINTS_PERSONA,
        }
        return persona_map.get(department, RECEPTION_PERSONA)

    def get_routing_message(
        self, routing_decision: RoutingDecision, language: str = "ar"
    ) -> str:
        """
        Get appropriate routing message based on decision
        """
        prompts = get_prompts(language)

        if routing_decision.department == Department.SALES:
            return prompts.get(
                "routing_to_sales", "You will be routed to sales. Please wait."
            )

        if routing_decision.department == Department.COMPLAINTS:
            return prompts.get(
                "routing_to_complaints",
                "You will be routed to complaints. Please wait.",
            )

        return prompts.get(
            "hold_message", "Thank you for waiting. An agent will be available soon."
        )

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def validate_input(
        self, stage: IVRStage, user_input: str, language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Validate user input for current stage
        Returns: {"valid": bool, "cleaned": str, "error": Optional[str]}
        """
        prompts = get_prompts(language)

        if not user_input or not user_input.strip():
            return {
                "valid": False,
                "error": prompts.get(
                    "invalid_input", "Invalid input. Please try again."
                ),
            }

        # Map stage to field for validation
        stage_field_mapping = {
            IVRStage.COLLECT_NAME: "name",
            IVRStage.COLLECT_PHONE: "phone",
            IVRStage.COLLECT_EMAIL: "email",
            IVRStage.COLLECT_SERVICE_TYPE: "service_type",
        }

        field = stage_field_mapping.get(stage)
        if field:
            return self.rules_engine.validate_field(field, user_input)

        return {"valid": True, "cleaned": user_input.strip()}

    def handle_invalid_input(
        self, stage: IVRStage, retry_count: int, language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Handle invalid input based on retry count
        """
        prompts = get_prompts(language)
        max_retries = self.rules_engine.rules.get("reception_rules", {}).get(
            "confirmation_retries", 2
        )

        if retry_count >= max_retries:
            return {
                "should_transfer": True,
                "message": prompts.get(
                    "max_retries",
                    "We could not collect information. Connecting to representative.",
                ),
                "next_stage": IVRStage.DEPARTMENT_HANDLING,
            }

        return {
            "should_transfer": False,
            "message": prompts.get(
                "invalid_input", "Invalid input. Please try again."
            ),
            "retry_count": retry_count + 1,
        }

    # ========================================================================
    # CONFIRMATION LOGIC
    # ========================================================================

    def process_confirmation(
        self, response: str, language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Process confirmation response (1 for confirm, 2 for edit)
        """
        prompts = get_prompts(language)

        if response.strip() in ["1", "yes", "نعم"]:
            return {
                "confirmed": True,
                "next_stage": IVRStage.ROUTE_TO_DEPARTMENT,
            }

        elif response.strip() in ["2", "no", "لا"]:
            return {
                "confirmed": False,
                "next_stage": IVRStage.COLLECT_NAME,  # Start over
                "message": prompts.get(
                    "greeting", "Let's collect your information again."
                ),
            }

        return {
            "confirmed": False,
            "next_stage": IVRStage.CONFIRM_DATA,
            "error": prompts.get("invalid_input", "Please press 1 or 2"),
        }

    # ========================================================================
    # CALL STATE MANAGEMENT
    # ========================================================================

    def initialize_call(self, call_id: str, phone_number: str) -> Call:
        """
        Initialize a new call
        """
        return Call(
            call_id=call_id,
            phone_number=phone_number,
            ivr_stage=IVRStage.WELCOME,
            started_at=datetime.now(),
        )

    def update_call_stage(
        self, call: Call, new_stage: IVRStage, data: Optional[Dict] = None
    ) -> Call:
        """
        Update call with new stage and collected data
        """
        call.ivr_stage = new_stage

        if data:
            call.collected_data.update(data)

        call.updated_at = datetime.now()

        return call

    def finalize_call(self, call: Call) -> Call:
        """
        Finalize call and prepare for end
        """
        call.ivr_stage = IVRStage.CALL_ENDED
        call.ended_at = datetime.now()

        # Calculate duration
        if call.started_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            call.total_duration_seconds = int(duration)

        return call

    # ========================================================================
    # DECISION TREES
    # ========================================================================

    def should_require_confirmation(self) -> bool:
        """Check if data confirmation is required"""
        return self.rules_engine.should_require_data_confirmation()

    def get_confirmation_retries(self) -> int:
        """Get number of confirmation retries"""
        return self.rules_engine.get_confirmation_retries()

    def get_max_ivr_retries(self) -> int:
        """Get max retries for IVR input collection"""
        from .config import IVR_MAX_RETRIES

        return IVR_MAX_RETRIES


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_router = None


def get_call_router() -> CallRouter:
    """Get or create call router instance"""
    global _router
    if _router is None:
        _router = CallRouter()
    return _router


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "CallRouter",
    "get_call_router",
]
