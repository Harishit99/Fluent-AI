import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GrammarQuestion(Base):
    __tablename__ = "grammar_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic = Column(String(80), nullable=False, index=True)  # tenses, articles, prepositions, subject_verb_agreement, etc.
    cefr_level = Column(String(10), nullable=False, default="A2")  # A1, A2, B1, B2, C1, C2
    question_type = Column(String(40), nullable=False, default="multiple_choice")  # multiple_choice, fill_blank, sentence_correction, sentence_ordering
    prompt = Column(Text, nullable=False)
    options_json = Column(Text, nullable=True)  # JSON-encoded array of options
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    is_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(80), nullable=False)
    cefr_level = Column(String(10), nullable=False, default="A2")
    test_mode = Column(String(30), default="standard")  # quick_5, standard_10, challenge_20, custom, revision
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    time_taken_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="test_attempts")
    responses = relationship("TestResponse", back_populates="attempt", cascade="all, delete-orphan")


class TestResponse(Base):
    __tablename__ = "test_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), nullable=False)
    question_prompt = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    attempt = relationship("TestAttempt", back_populates="responses")
