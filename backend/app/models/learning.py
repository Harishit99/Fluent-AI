import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SkillProgress(Base):
    __tablename__ = "skill_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(50), nullable=False)  # grammar, vocabulary, speaking, listening, pronunciation
    estimated_level = Column(String(10), default="A2")  # A1, A2, B1, B2, C1, C2
    accuracy_percentage = Column(Float, default=70.0)
    total_attempts = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0 based on sample size
    last_practiced_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="skill_progress")


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    target_minutes = Column(Integer, default=20)
    completed_minutes = Column(Integer, default=0)
    activities_json = Column(Text, nullable=False)  # JSON array of activities
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="learning_plans")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_key = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    unlocked_at = Column(DateTime, default=utc_now)
