import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile, LearningPreferences
from app.models.learning import SkillProgress, LearningPlan
from app.models.mistake import CorrectionRecord
from app.models.test import TestAttempt
from app.models.vocabulary import VocabularyItem, VocabularyReview
from app.schemas.learning import LearningPlanOut, ActivityItem, WeeklyReportOut, SkillProgressOut, WeeklyDayStat
from app.services.adaptive_learning.engine import AdaptiveLearningEngine
from app.services.ai.manager import ai_manager

router = APIRouter(prefix="", tags=["learning"])


@router.get("/learning-plan", response_model=LearningPlanOut)
def get_daily_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    plan = (
        db.query(LearningPlan)
        .filter(LearningPlan.user_id == current_user.id, LearningPlan.plan_date == today_str)
        .first()
    )

    if not plan:
        prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
        target_mins = prefs.daily_time_target_mins if prefs else 20

        generated = AdaptiveLearningEngine.generate_daily_plan(
            db=db,
            user_id=current_user.id,
            target_minutes=target_mins,
        )
        plan = LearningPlan(
            user_id=current_user.id,
            plan_date=today_str,
            target_minutes=target_mins,
            activities_json=json.dumps(generated["activities"]),
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

    raw_activities = json.loads(plan.activities_json)
    return LearningPlanOut(
        id=plan.id,
        plan_date=plan.plan_date,
        target_minutes=plan.target_minutes,
        completed_minutes=plan.completed_minutes,
        is_completed=plan.is_completed,
        activities=[ActivityItem(**a) for a in raw_activities],
    )


@router.post("/learning-plan/generate", response_model=LearningPlanOut)
def regenerate_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
    target_mins = prefs.daily_time_target_mins if prefs else 20

    generated = AdaptiveLearningEngine.generate_daily_plan(
        db=db,
        user_id=current_user.id,
        target_minutes=target_mins,
    )

    plan = (
        db.query(LearningPlan)
        .filter(LearningPlan.user_id == current_user.id, LearningPlan.plan_date == today_str)
        .first()
    )
    if not plan:
        plan = LearningPlan(user_id=current_user.id, plan_date=today_str)
        db.add(plan)

    plan.target_minutes = target_mins
    plan.activities_json = json.dumps(generated["activities"])
    db.commit()
    db.refresh(plan)

    raw_activities = json.loads(plan.activities_json)
    return LearningPlanOut(
        id=plan.id,
        plan_date=plan.plan_date,
        target_minutes=plan.target_minutes,
        completed_minutes=plan.completed_minutes,
        is_completed=plan.is_completed,
        activities=[ActivityItem(**a) for a in raw_activities],
    )


@router.get("/reports/weekly", response_model=WeeklyReportOut)
def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve user's actual attempts and records
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    streak = profile.streak_count if profile else 1
    total_mins = profile.total_minutes_practiced if profile else 0

    # Tests completed
    attempts = db.query(TestAttempt).filter(TestAttempt.user_id == current_user.id, TestAttempt.completed == True).all()
    test_count = len(attempts)
    avg_accuracy = round(sum(a.score_percentage for a in attempts) / test_count, 1) if test_count > 0 else 72.0

    # Skills breakdown
    skills = db.query(SkillProgress).filter(SkillProgress.user_id == current_user.id).all()
    skill_schemas = [
        SkillProgressOut(
            id=s.id,
            skill_name=s.skill_name,
            estimated_level=s.estimated_level,
            accuracy_percentage=s.accuracy_percentage,
            total_attempts=s.total_attempts,
            confidence_score=s.confidence_score,
            last_practiced_at=s.last_practiced_at,
        )
        for s in skills
    ]

    # Common mistakes breakdown
    mistakes = (
        db.query(CorrectionRecord.category, func.count(CorrectionRecord.id).label("count"))
        .filter(CorrectionRecord.user_id == current_user.id)
        .group_by(CorrectionRecord.category)
        .order_by(func.count(CorrectionRecord.id).desc())
        .limit(5)
        .all()
    )
    common_cats = [{"category": c[0], "count": c[1]} for c in mistakes]

    # Daily activity past 7 days
    today = datetime.now(timezone.utc)
    daily_stats: List[WeeklyDayStat] = []
    days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        day_name = days_abbr[d.weekday()]

        # Compute tests on day
        tests_on_day = sum(1 for a in attempts if a.started_at and a.started_at.strftime("%Y-%m-%d") == d_str)
        daily_stats.append(WeeklyDayStat(
            day=day_name,
            date=d_str,
            minutes_practiced=max(5, tests_on_day * 4) if tests_on_day > 0 else 0,
            tests_completed=tests_on_day,
            words_reviewed=max(0, tests_on_day * 2),
        ))

    rec_focus = "Verb Tenses & Consistency" if common_cats else "Natural Conversational Phrasing"
    rec_reason = (
        f"Based on {common_cats[0]['count']} error detections in your speaking practice."
        if common_cats
        else "Continue balanced daily practice across speaking and listening."
    )

    return WeeklyReportOut(
        total_minutes_week=max(total_mins, sum(d.minutes_practiced for d in daily_stats)),
        total_tests_completed=test_count,
        average_accuracy=avg_accuracy,
        streak_count=streak,
        common_mistakes_categories=common_cats,
        skills_breakdown=skill_schemas,
        daily_activity=daily_stats,
        recommended_focus=rec_focus,
        recommendation_reason=rec_reason,
    )


@router.post("/learning/hinglish")
def translate_hinglish(
    sentence: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Translates Hinglish/Hindi thought to natural English with pedagogical explanation."""
    llm = ai_manager.provider
    result = llm.translate_and_explain_hinglish(sentence)
    return result
