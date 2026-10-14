from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    audio_url: Optional[str] = None


class CorrectionItem(BaseModel):
    original: str
    corrected: str
    category: str
    explanation: str
    natural_alternative: Optional[str] = None
    severity: str = "important"
    practice_recommended: bool = True


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    audio_url: Optional[str] = None
    created_at: datetime
    corrections: Optional[List[CorrectionItem]] = None

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    mode: str = Field("free", description="instant, natural, fluency, interview, roleplay, free")
    topic: str = Field("Everyday Life", max_length=150)


class ConversationFinish(BaseModel):
    summary: Optional[str] = None


class ConversationOut(BaseModel):
    id: str
    user_id: str
    mode: str
    topic: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    summary: Optional[str] = None
    feedback_notes: Optional[str] = None
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True
