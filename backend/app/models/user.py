import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("LearningPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    mistakes = relationship("CorrectionRecord", back_populates="user", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete-orphan")
    vocabulary = relationship("VocabularyItem", back_populates="user", cascade="all, delete-orphan")
    skill_progress = relationship("SkillProgress", back_populates="user", cascade="all, delete-orphan")
    learning_plans = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False, default="English Learner")
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    streak_count = Column(Integer, default=1)
    last_active_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    total_minutes_practiced = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="profile")


class LearningPreferences(Base):
    __tablename__ = "learning_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    current_level = Column(String(10), default="A2")  # A1, A2, B1, B2, C1, C2
    target_goal = Column(String(100), default="Daily conversation & fluency")
    explanation_language = Column(String(20), default="en")  # 'en' or 'hi'
    daily_time_target_mins = Column(Integer, default=15)
    primary_difficulty = Column(String(100), default="Forming natural sentences quickly")
    correction_style = Column(String(50), default="instant")  # 'instant', 'natural', 'fluency'
    voice_speed = Column(String(20), default="normal")  # 'slow', 'normal', 'fast'
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="preferences")
