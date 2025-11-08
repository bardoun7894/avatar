#!/usr/bin/env python3
"""
Call Center Data Models
Extends avatary models with call center specific entities
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS FOR CALL CENTER
# ============================================================================

class CallStatus(str, Enum):
    """Call status throughout its lifecycle"""
    INITIATED = "initiated"
    IVR_PROCESSING = "ivr_processing"
    IN_QUEUE = "in_queue"
    IN_PROGRESS = "in_progress"
    TRANSFERRED = "transferred"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


class CallDirection(str, Enum):
    """Call direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Department(str, Enum):
    """Call center departments"""
    RECEPTION = "reception"
    SALES = "sales"
    COMPLAINTS = "complaints"


class TicketStatus(str, Enum):
    """Ticket status in CRM"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Ticket priority level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class IVRStage(str, Enum):
    """IVR interaction stages"""
    WELCOME = "welcome"
    COLLECT_NAME = "collect_name"
    COLLECT_PHONE = "collect_phone"
    COLLECT_EMAIL = "collect_email"
    COLLECT_SERVICE_TYPE = "collect_service_type"
    CONFIRM_DATA = "confirm_data"
    ROUTE_TO_DEPARTMENT = "route_to_department"
    DEPARTMENT_HANDLING = "department_handling"
    CALL_ENDED = "call_ended"


# ============================================================================
# CALL MODELS
# ============================================================================

class CallMetadata(BaseModel):
    """Metadata for a call"""
    source: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class CallBase(BaseModel):
    """Base call information"""
    phone_number: Optional[str] = None
    direction: CallDirection = CallDirection.INBOUND
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None


class Call(CallBase):
    """Full call model"""
    call_id: str = Field(..., description="Unique call identifier")
    status: CallStatus = Field(default=CallStatus.INITIATED)
    department: Optional[Department] = None
    service_type: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    ivr_stage: IVRStage = Field(default=IVRStage.WELCOME)

    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    queue_time_seconds: int = Field(default=0)
    talk_time_seconds: int = Field(default=0)
    total_duration_seconds: int = Field(default=0)

    # Data collection
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: CallMetadata = Field(default_factory=CallMetadata)

    # IVR/Bot responses
    bot_response_count: int = Field(default=0)
    transferred_to_agent: bool = Field(default=False)

    class Config:
        from_attributes = True


# ============================================================================
# TICKET MODELS (CRM)
# ============================================================================

class TicketBase(BaseModel):
    """Base ticket information"""
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=8)
    customer_email: Optional[EmailStr] = None
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class Ticket(TicketBase):
    """Full ticket model"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    call_id: Optional[str] = None
    department: Department = Department.COMPLAINTS
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)

    assigned_to: Optional[str] = None  # Agent ID
    assigned_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ============================================================================
# AGENT/REPRESENTATIVE MODELS
# ============================================================================

class AgentStatus(str, Enum):
    """Agent availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    ON_BREAK = "on_break"
    OFFLINE = "offline"


class Agent(BaseModel):
    """Agent/representative information"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Department = Department.RECEPTION
    status: AgentStatus = Field(default=AgentStatus.OFFLINE)

    # Skills and limits
    skills: List[str] = Field(default_factory=list)
    max_concurrent_calls: int = Field(default=1, ge=1, le=10)
    current_call_count: int = Field(default=0)

    # Stats
    total_calls_handled: int = Field(default=0)
    avg_handling_time_seconds: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.now)
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER INTERACTION HISTORY
# ============================================================================

class CustomerProfile(BaseModel):
    """Customer profile for CRM"""
    customer_id: str = Field(..., description="Unique customer identifier")
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    email: Optional[EmailStr] = None

    # Interaction history
    total_calls: int = Field(default=0)
    total_tickets: int = Field(default=0)
    last_interaction: Optional[datetime] = None

    # Contact details
    company_name: Optional[str] = None
    address: Optional[str] = None

    # Notes
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


# ============================================================================
# TRANSCRIPT MODELS
# ============================================================================

class TranscriptMessage(BaseModel):
    """Single message in a call transcript"""
    timestamp: datetime = Field(default_factory=datetime.now)
    speaker: Literal["customer", "agent", "bot", "system"]
    content: str = Field(..., min_length=1)
    language: Optional[str] = None  # "ar" or "en"


class CallTranscript(BaseModel):
    """Complete call transcript"""
    call_id: str = Field(..., description="Reference to call_id")
    customer_name: Optional[str] = None
    agent_name: Optional[str] = None
    department: Optional[Department] = None
    messages: List[TranscriptMessage] = Field(default_factory=list)
    sentiment: Optional[str] = None  # "positive", "neutral", "negative"
    summary: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS & REPORTING MODELS
# ============================================================================

class DepartmentStats(BaseModel):
    """Statistics for a department"""
    department: Department
    total_calls: int = Field(default=0)
    avg_wait_time_seconds: int = Field(default=0)
    avg_handling_time_seconds: int = Field(default=0)
    calls_transferred: int = Field(default=0)
    customer_satisfaction_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    peak_hour: Optional[str] = None


class AgentPerformance(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    calls_handled: int = Field(default=0)
    avg_call_duration_seconds: int = Field(default=0)
    customer_satisfaction_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    tickets_created: int = Field(default=0)
    tickets_resolved: int = Field(default=0)
    escalation_rate: float = Field(default=0.0, ge=0.0, le=100.0)


class CallQueueStats(BaseModel):
    """Real-time call queue statistics"""
    total_calls_in_queue: int = Field(default=0)
    avg_wait_time_seconds: int = Field(default=0)
    longest_wait_time_seconds: int = Field(default=0)
    available_agents: int = Field(default=0)
    busy_agents: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class CallStartResponse(BaseModel):
    """Response when starting a call"""
    success: bool
    call_id: str
    message: str
    welcome_message: str


class IVRStageResponse(BaseModel):
    """Response for IVR stage"""
    current_stage: IVRStage
    prompt: str
    language: Literal["ar", "en"]
    expected_input: Optional[str] = None


class RoutingDecision(BaseModel):
    """Decision made by routing engine"""
    department: Department
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternative_departments: List[Department] = Field(default_factory=list)


# ============================================================================
# EXPORT ALL MODELS
# ============================================================================

__all__ = [
    # Enums
    "CallStatus",
    "CallDirection",
    "Department",
    "TicketStatus",
    "TicketPriority",
    "IVRStage",
    "AgentStatus",

    # Call models
    "CallMetadata",
    "CallBase",
    "Call",

    # Ticket models
    "TicketBase",
    "Ticket",

    # Agent models
    "Agent",
    "CustomerProfile",

    # Transcript models
    "TranscriptMessage",
    "CallTranscript",

    # Analytics models
    "DepartmentStats",
    "AgentPerformance",
    "CallQueueStats",

    # Response models
    "CallStartResponse",
    "IVRStageResponse",
    "RoutingDecision",
]
