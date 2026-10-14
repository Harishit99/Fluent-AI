from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile, LearningPreferences
from app.models.learning import SkillProgress
from app.models.test import TestAttempt
from app.models.mistake import CorrectionRecord
from app.models.vocabulary import VocabularyItem

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("")
def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
    skills = db.query(SkillProgress).filter(SkillProgress.user_id == current_user.id).all()
    attempts = db.query(TestAttempt).filter(TestAttempt.user_id == current_user.id, TestAttempt.completed == True).all()
    mistakes = db.query(CorrectionRecord).filter(CorrectionRecord.user_id == current_user.id).all()
    vocab_count = db.query(VocabularyItem).filter(VocabularyItem.user_id == current_user.id).count()

    # Calculate overall CEFR level
    skill_map = {s.skill_name: s for s in skills}
    current_level = prefs.current_level if prefs else "A2"
    if skill_map.get("grammar"):
        current_level = skill_map["grammar"].estimated_level

    # Accuracy calculations
    total_tests = len(attempts)
    avg_accuracy = round(sum(a.score_percentage for a in attempts) / total_tests, 1) if total_tests > 0 else 70.0

    # Skill radar data
    radar_data = [
        {"skill": "Grammar", "score": skill_map.get("grammar").accuracy_percentage if "grammar" in skill_map else 68.0, "level": skill_map.get("grammar").estimated_level if "grammar" in skill_map else "A2"},
        {"skill": "Vocabulary", "score": skill_map.get("vocabulary").accuracy_percentage if "vocabulary" in skill_map else 72.0, "level": skill_map.get("vocabulary").estimated_level if "vocabulary" in skill_map else "B1"},
        {"skill": "Speaking", "score": skill_map.get("speaking").accuracy_percentage if "speaking" in skill_map else 65.0, "level": skill_map.get("speaking").estimated_level if "speaking" in skill_map else "A2"},
        {"skill": "Listening", "score": skill_map.get("listening").accuracy_percentage if "listening" in skill_map else 75.0, "level": skill_map.get("listening").estimated_level if "listening" in skill_map else "B1"},
        {"skill": "Pronunciation", "score": skill_map.get("pronunciation").accuracy_percentage if "pronunciation" in skill_map else 70.0, "level": skill_map.get("pronunciation").estimated_level if "pronunciation" in skill_map else "A2"},
    ]

    return {
        "current_level": current_level,
        "target_goal": prefs.target_goal if prefs else "Fluent English",
        "streak_count": profile.streak_count if profile else 1,
        "total_minutes_practiced": profile.total_minutes_practiced if profile else 0,
        "total_tests_completed": total_tests,
        "overall_accuracy": avg_accuracy,
        "vocabulary_saved": vocab_count,
        "active_mistakes_count": len([m for m in mistakes if m.mastery_status != "mastered"]),
        "mastered_mistakes_count": len([m for m in mistakes if m.mastery_status == "mastered"]),
        "radar_skills": radar_data,
        "recent_mistakes": [
            {
                "id": m.id,
                "original": m.original_sentence,
                "corrected": m.corrected_sentence,
                "category": m.category,
                "mastery_status": m.mastery_status,
            }
            for m in mistakes[:4]
        ],
    }
