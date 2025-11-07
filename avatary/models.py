#!/usr/bin/env python3
"""
Pydantic Models for Avatar App
Centralizes all data models for type safety and validation
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, time
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ConsultationStatus(str, Enum):
    """Consultation status options"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class MeetingType(str, Enum):
    """Meeting type options"""
    ONLINE = "online"
    IN_PERSON = "in_person"
    PHONE = "phone"


class InquiryStatus(str, Enum):
    """Inquiry status options"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"
    CLOSED = "closed"


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# USER MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user information"""
    name: str = Field(..., min_length=1, description="User's full name")
    phone: str = Field(..., min_length=8, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        # Remove spaces and common prefixes
        cleaned = v.replace(" ", "").replace("+", "")
        if not cleaned.isdigit() or len(cleaned) < 8:
            raise ValueError('Invalid phone number format')
        return v


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class User(UserBase):
    """Full user model with database fields"""
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_interaction: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


# ============================================================================
# CONSULTATION MODELS
# ============================================================================

class ConsultationBase(BaseModel):
    """Base consultation information"""
    customer_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    service_type: str = Field(..., description="Type of service requested")
    consultation_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date in YYYY-MM-DD format")
    consultation_time: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="Time in HH:MM format")
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    notes: Optional[str] = None
    meeting_type: MeetingType = Field(default=MeetingType.ONLINE)
    duration_minutes: int = Field(default=30, ge=15, le=240)


class ConsultationCreate(ConsultationBase):
    """Model for creating a consultation"""
    pass


class Consultation(ConsultationBase):
    """Full consultation model"""
    consultation_id: str = Field(..., pattern=r'^CON\d{4}$')
    status: ConsultationStatus = Field(default=ConsultationStatus.SCHEDULED)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AvailableSlots(BaseModel):
    """Available consultation time slots"""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    slots: List[str] = Field(..., description="List of available times in HH:MM format")
    business_hours: Dict[str, str] = Field(default={"start": "09:00", "end": "18:00"})


# ============================================================================
# INQUIRY MODELS
# ============================================================================

class InquiryBase(BaseModel):
    """Base inquiry information"""
    customer_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    inquiry_type: str = Field(..., description="Type of inquiry")
    message: str = Field(..., min_length=1, description="Inquiry message")
    email: Optional[EmailStr] = None


class InquiryCreate(InquiryBase):
    """Model for creating an inquiry"""
    pass


class Inquiry(InquiryBase):
    """Full inquiry model"""
    inquiry_id: str = Field(..., pattern=r'^INQ\d{4}$')
    status: InquiryStatus = Field(default=InquiryStatus.NEW)
    response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# TRAINING MODELS
# ============================================================================

class TrainingBase(BaseModel):
    """Base training enrollment information"""
    participant_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    program_name: str = Field(..., description="Training program name")
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    experience_level: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced")
    notes: Optional[str] = None


class TrainingCreate(TrainingBase):
    """Model for creating training enrollment"""
    pass


class Training(TrainingBase):
    """Full training enrollment model"""
    enrollment_id: str = Field(..., pattern=r'^TRN\d{4}$')
    status: str = Field(default="registered")
    payment_status: Optional[str] = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# CONVERSATION MODELS
# ============================================================================

class Message(BaseModel):
    """Single message in a conversation"""
    role: MessageRole
    content: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation information"""
    conversation_id: str = Field(..., min_length=1)
    room_name: Optional[str] = None
    participant_identity: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Model for creating a conversation"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Conversation(ConversationBase):
    """Full conversation model with messages"""
    messages: List[Message] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    message_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.message_count = len(self.messages)
        return message

    def get_message_summary(self) -> Dict[str, int]:
        """Get summary of messages by role"""
        summary = {role.value: 0 for role in MessageRole}
        for msg in self.messages:
            summary[msg.role.value] += 1
        return summary

    class Config:
        from_attributes = True


# ============================================================================
# VISUAL CONTEXT MODELS (Already exist in visual_context_models.py)
# ============================================================================

# Note: VisualAnalysis and VisualContextStore are in visual_context_models.py
# Keeping them separate for modularity


# ============================================================================
# KNOWLEDGE BASE MODELS
# ============================================================================

class KnowledgeBaseItem(BaseModel):
    """Knowledge base item (FAQ, product, etc.)"""
    id: Optional[int] = None
    title: str
    content: str
    category: str
    tags: Optional[List[str]] = Field(default_factory=list)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """Search query for knowledge base"""
    query: str = Field(..., min_length=1)
    category: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)


class SearchResults(BaseModel):
    """Search results from knowledge base"""
    query: str
    results: List[KnowledgeBaseItem]
    total_count: int
    execution_time_ms: Optional[float] = None


# ============================================================================
# CONFIG MODELS
# ============================================================================

class BusinessHours(BaseModel):
    """Business operating hours"""
    start_time: time = Field(default=time(9, 0))
    end_time: time = Field(default=time(18, 0))
    days: List[str] = Field(default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

    def is_open(self, check_time: time = None) -> bool:
        """Check if currently within business hours"""
        if check_time is None:
            check_time = datetime.now().time()
        return self.start_time <= check_time <= self.end_time


class AppConfig(BaseModel):
    """Application configuration"""
    app_name: str = "Ornina Avatar"
    language: str = "ar"
    voice_provider: str = "openai"
    voice_model: str = "alloy"
    vision_enabled: bool = True
    vision_analysis_interval: int = Field(default=3, ge=1, le=30, description="Seconds between analyses")
    max_conversation_messages: int = Field(default=100, ge=10, le=1000)
    business_hours: BusinessHours = Field(default_factory=BusinessHours)


# ============================================================================
# RESPONSE MODELS (for API responses)
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[str] = None
    error_code: Optional[str] = None


# ============================================================================
# FACE RECOGNITION MODELS
# ============================================================================

class FaceEmbedding(BaseModel):
    """Face embedding vector for recognition"""
    user_id: Optional[int] = None
    user_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    embedding: List[float] = Field(..., description="Face embedding vector (128 or 512 dimensions)")
    image_url: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @validator('embedding')
    def validate_embedding_dimensions(cls, v):
        """Validate embedding has correct dimensions"""
        if len(v) not in [128, 512]:
            raise ValueError(f'Embedding must be 128 or 512 dimensions, got {len(v)}')
        return v

    class Config:
        from_attributes = True


class FaceMatch(BaseModel):
    """Result of face matching"""
    matched: bool = Field(default=False)
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Match confidence score")
    distance: float = Field(default=1.0, ge=0.0, description="Distance metric (lower = better match)")
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_high_confidence(self) -> bool:
        """Check if match has high confidence"""
        return self.confidence >= 0.85

    def to_message(self, language: str = "ar") -> str:
        """Convert match to user-friendly message"""
        if not self.matched:
            if language == "ar":
                return "لم أتمكن من التعرف على هذا الشخص. هل يمكنك تعريفني بنفسك؟"
            return "I don't recognize this person. Could you introduce yourself?"

        if language == "ar":
            return f"أهلاً {self.user_name}! أنا أراك وأتعرف عليك. كيف يمكنني مساعدتك اليوم؟"
        return f"Hello {self.user_name}! I see and recognize you. How can I help you today?"


class FaceRecognitionConfig(BaseModel):
    """Configuration for face recognition system"""
    enabled: bool = Field(default=True)
    recognition_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum distance threshold for match")
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence to accept match")
    max_faces_per_frame: int = Field(default=5, ge=1, le=20)
    recognition_interval_seconds: int = Field(default=5, ge=1, le=60)
    store_unknown_faces: bool = Field(default=False, description="Whether to store faces of unknown people")


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_arabic_text(text: str) -> bool:
    """Check if text contains Arabic characters"""
    return any('\u0600' <= char <= '\u06FF' for char in text)


def validate_date_format(date_str: str) -> bool:
    """Validate YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_time_format(time_str: str) -> bool:
    """Validate HH:MM format"""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


# ============================================================================
# EXPORT ALL MODELS
# ============================================================================

__all__ = [
    # Enums
    'ConsultationStatus',
    'MeetingType',
    'InquiryStatus',
    'MessageRole',

    # User models
    'UserBase',
    'UserCreate',
    'User',

    # Consultation models
    'ConsultationBase',
    'ConsultationCreate',
    'Consultation',
    'AvailableSlots',

    # Inquiry models
    'InquiryBase',
    'InquiryCreate',
    'Inquiry',

    # Training models
    'TrainingBase',
    'TrainingCreate',
    'Training',

    # Conversation models
    'Message',
    'ConversationBase',
    'ConversationCreate',
    'Conversation',

    # Knowledge Base models
    'KnowledgeBaseItem',
    'SearchQuery',
    'SearchResults',

    # Config models
    'BusinessHours',
    'AppConfig',

    # Response models
    'SuccessResponse',
    'ErrorResponse',

    # Validators
    'validate_arabic_text',
    'validate_date_format',
    'validate_time_format',
]
