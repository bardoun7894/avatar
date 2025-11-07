"""
Visual Context Models using Pydantic
Clean data models for managing visual analysis context
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VisualAnalysis(BaseModel):
    """Represents a single visual analysis from GPT-4 Vision"""

    content: str = Field(
        description="The visual analysis description in Arabic/English"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this analysis was created"
    )
    confidence: Optional[str] = Field(
        default=None,
        description="Confidence level (low/medium/high)"
    )

    @property
    def age_seconds(self) -> float:
        """Calculate how old this analysis is in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()

    @property
    def is_fresh(self) -> bool:
        """Check if analysis is fresh (less than 10 seconds old)"""
        return self.age_seconds < 10

    def to_injection_text(self) -> str:
        """Format for LLM context injection"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"""
[SYSTEM - VISUAL CONTEXT]
وقت التحديث: {time_str} | Updated: {time_str}

أنت تستطيع رؤية المستخدم الآن من خلال الكاميرا!
YOU CAN NOW SEE THE USER THROUGH THE CAMERA!

ما تراه:
{self.content}

⚠️ مهم جداً: استخدم ما تراه في ردك! اذكر للمستخدم أنك تراه!
VERY IMPORTANT: Use what you see in your response! Tell the user you can see them!

[END VISUAL CONTEXT]
"""


class VisualContextStore(BaseModel):
    """Thread-safe store for visual context"""

    latest_analysis: Optional[VisualAnalysis] = Field(
        default=None,
        description="Most recent visual analysis"
    )
    enabled: bool = Field(
        default=True,
        description="Whether visual context injection is enabled"
    )
    max_age_seconds: float = Field(
        default=15.0,
        description="Maximum age for context to be considered valid"
    )

    def update(self, content: str, confidence: Optional[str] = None) -> VisualAnalysis:
        """Update with new analysis"""
        analysis = VisualAnalysis(
            content=content,
            confidence=confidence
        )
        self.latest_analysis = analysis
        return analysis

    def get_current(self) -> Optional[VisualAnalysis]:
        """Get current analysis if fresh enough"""
        if not self.enabled or not self.latest_analysis:
            return None

        if self.latest_analysis.age_seconds > self.max_age_seconds:
            return None

        return self.latest_analysis

    def clear(self):
        """Clear current analysis"""
        self.latest_analysis = None

    class Config:
        """Pydantic config"""
        validate_assignment = True
        arbitrary_types_allowed = True
