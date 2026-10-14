from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillProgressOut(BaseModel):
    id: str
    skill_name: str
    estimated_level: str
    accuracy_percentage: float
    total_attempts: int
    confidence_score: float
    last_practiced_at: datetime

    class Config:
        from_attributes = True


class ActivityItem(BaseModel):
    id: str
    title: str
    type: str  # conversation, grammar, vocabulary, listening, mistakes
    target_minutes: int
    completed_minutes: int
    is_completed: bool
    description: str


class LearningPlanOut(BaseModel):
    id: str
    plan_date: str
    target_minutes: int
    completed_minutes: int
    is_completed: bool
    activities: List[ActivityItem] = []


class WeeklyDayStat(BaseModel):
    day: str
    date: str
    minutes_practiced: int
    tests_completed: int
    words_reviewed: int


class WeeklyReportOut(BaseModel):
    total_minutes_week: int
    total_tests_completed: int
    average_accuracy: float
    streak_count: int
    common_mistakes_categories: List[Dict[str, Any]]
    skills_breakdown: List[SkillProgressOut]
    daily_activity: List[WeeklyDayStat]
    recommended_focus: str
    recommendation_reason: str
