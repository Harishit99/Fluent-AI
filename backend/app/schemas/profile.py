from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    id: str
    user_id: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    streak_count: int
    last_active_date: Optional[str] = None
    total_minutes_practiced: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class PreferencesOut(BaseModel):
    id: str
    user_id: str
    current_level: str
    target_goal: str
    explanation_language: str
    daily_time_target_mins: int
    primary_difficulty: str
    correction_style: str
    voice_speed: str

    class Config:
        from_attributes = True


class PreferencesUpdate(BaseModel):
    current_level: Optional[str] = None
    target_goal: Optional[str] = None
    explanation_language: Optional[str] = None
    daily_time_target_mins: Optional[int] = Field(None, ge=5, le=120)
    primary_difficulty: Optional[str] = None
    correction_style: Optional[str] = None
    voice_speed: Optional[str] = None
