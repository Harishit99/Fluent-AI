import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CorrectionRecord(Base):
    __tablename__ = "correction_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    original_sentence = Column(Text, nullable=False)
    corrected_sentence = Column(Text, nullable=False)
    category = Column(String(80), nullable=False, index=True)  # verb_tense, subject_verb_agreement, articles, prepositions, etc.
    explanation = Column(Text, nullable=False)
    natural_alternative = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)
    severity = Column(String(20), default="important")  # minor, important, critical
    
    occurrence_count = Column(Integer, default=1)
    repetition_revisions = Column(Integer, default=0)
    mastery_status = Column(String(30), default="learning")  # learning, understood, mastered
    practice_recommended = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=utc_now)
    last_practiced_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="mistakes")
    conversation = relationship("Conversation", back_populates="mistakes")
