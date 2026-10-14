import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word = Column(String(100), nullable=False, index=True)
    meaning = Column(Text, nullable=False)
    part_of_speech = Column(String(30), nullable=True)  # noun, verb, adjective, adverb, idiom
    example_sentence = Column(Text, nullable=False)
    hindi_translation = Column(String(200), nullable=True)
    synonyms_json = Column(Text, nullable=True)  # JSON array
    antonyms_json = Column(Text, nullable=True)  # JSON array
    cefr_level = Column(String(10), default="B1")
    mastery_status = Column(String(30), default="learning")  # learning, reviewing, mastered
    user_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="vocabulary")
    review = relationship("VocabularyReview", back_populates="item", uselist=False, cascade="all, delete-orphan")


class VocabularyReview(Base):
    """Spaced Repetition System (SRS) Leitner/SuperMemo tracker."""
    __tablename__ = "vocabulary_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(36), ForeignKey("vocabulary_items.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    repetition_count = Column(Integer, default=0)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    last_reviewed_at = Column(DateTime, default=utc_now)
    next_review_date = Column(DateTime, default=utc_now)

    item = relationship("VocabularyItem", back_populates="review")
