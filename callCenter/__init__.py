#!/usr/bin/env python3
"""
Call Center System
Intelligent voice-based call center with IVR, routing, and CRM
"""

from .config import (
    CALL_CENTER_MODE,
    COMPANY_NAME,
    is_call_center_enabled,
    should_override_avatary,
)
from .models import (
    Call,
    CallStatus,
    Department,
    Ticket,
    TicketStatus,
    Agent,
    CustomerProfile,
)
from .rules_engine import RulesEngine, get_rules_engine
from .call_router import CallRouter, get_call_router
from .crm_system import CRMSystem, get_crm_system

__version__ = "1.0.0"
__author__ = "Call Center Team"

__all__ = [
    # Config
    "CALL_CENTER_MODE",
    "COMPANY_NAME",
    "is_call_center_enabled",
    "should_override_avatary",

    # Models
    "Call",
    "CallStatus",
    "Department",
    "Ticket",
    "TicketStatus",
    "Agent",
    "CustomerProfile",

    # Rules Engine
    "RulesEngine",
    "get_rules_engine",

    # Router
    "CallRouter",
    "get_call_router",

    # CRM
    "CRMSystem",
    "get_crm_system",
]
