from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CorrectionOut(BaseModel):
    id: str
    user_id: str
    conversation_id: Optional[str] = None
    original_sentence: str
    corrected_sentence: str
    category: str
    explanation: str
    natural_alternative: Optional[str] = None
    example_sentence: Optional[str] = None
    severity: str
    occurrence_count: int
    repetition_revisions: int
    mastery_status: str
    practice_recommended: bool
    created_at: datetime
    last_practiced_at: datetime

    class Config:
        from_attributes = True


class CorrectionUpdate(BaseModel):
    mastery_status: Optional[str] = Field(None, description="learning, understood, mastered")
    practice_recommended: Optional[bool] = None


class CorrectionPracticeRequest(BaseModel):
    user_repetition_sentence: str
