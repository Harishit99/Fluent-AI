import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.learning import SkillProgress, LearningPlan
from app.models.mistake import CorrectionRecord
from app.models.test import TestAttempt
from app.models.vocabulary import VocabularyItem, VocabularyReview


CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


class AdaptiveLearningEngine:
    """
    Pedagogical engine calculating real skill estimations, Leitner spaced repetition,
    and adaptive daily curriculum recommendations.
    """

    @staticmethod
    def smooth_skill_update(
        current_level: str,
        current_accuracy: float,
        total_attempts: int,
        latest_score: float,
    ) -> Dict[str, Any]:
        """
        Applies exponential moving average smoothing to prevent erratic jumps.
        Considers progression only after sufficient confidence (e.g. >= 5 attempts)
        and sustained >= 90% performance.
        """
        # Weighting: 75% historical, 25% latest
        new_accuracy = round((current_accuracy * 0.75) + (latest_score * 0.25), 1)
        new_attempts = total_attempts + 1
        confidence = min(1.0, round(new_attempts / 10.0, 2))

        curr_idx = CEFR_ORDER.index(current_level) if current_level in CEFR_ORDER else 1
        new_level = current_level

        # Progression logic
        if new_attempts >= 5 and new_accuracy >= 88.0 and curr_idx < len(CEFR_ORDER) - 1:
            new_level = CEFR_ORDER[curr_idx + 1]
        elif new_attempts >= 5 and new_accuracy < 55.0 and curr_idx > 0:
            new_level = CEFR_ORDER[curr_idx - 1]

        return {
            "estimated_level": new_level,
            "accuracy_percentage": new_accuracy,
            "total_attempts": new_attempts,
            "confidence_score": confidence,
        }

    @staticmethod
    def calculate_srs_next_review(
        rating: int,  # 1 to 5
        repetition_count: int,
        interval_days: int,
        ease_factor: float,
    ) -> Dict[str, Any]:
        """
        SuperMemo SM-2 Spaced Repetition Algorithm.
        """
        if rating < 3:
            # Failed recall: reset repetitions, review tomorrow
            return {
                "repetition_count": 0,
                "interval_days": 1,
                "ease_factor": max(1.3, ease_factor - 0.2),
                "next_review_date": datetime.now(timezone.utc) + timedelta(days=1),
            }

        # Successful recall
        if repetition_count == 0:
            new_interval = 1
        elif repetition_count == 1:
            new_interval = 3
        else:
            new_interval = int(interval_days * ease_factor)

        # Update ease factor
        new_ef = ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
        new_ef = max(1.3, round(new_ef, 2))

        return {
            "repetition_count": repetition_count + 1,
            "interval_days": new_interval,
            "ease_factor": new_ef,
            "next_review_date": datetime.now(timezone.utc) + timedelta(days=new_interval),
        }

    @staticmethod
    def generate_daily_plan(
        db: Session,
        user_id: str,
        target_minutes: int = 20,
    ) -> Dict[str, Any]:
        """
        Generates a personalized daily curriculum based on the user's
        actual weaknesses, mistake notebook, and SRS queue.
        """
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. Check for recurring mistakes
        frequent_mistakes = (
            db.query(CorrectionRecord)
            .filter(CorrectionRecord.user_id == user_id, CorrectionRecord.mastery_status != "mastered")
            .order_by(CorrectionRecord.occurrence_count.desc())
            .limit(3)
            .all()
        )

        # 2. Check due vocabulary reviews
        due_vocab_count = (
            db.query(VocabularyReview)
            .join(VocabularyItem)
            .filter(
                VocabularyItem.user_id == user_id,
                VocabularyReview.next_review_date <= datetime.now(timezone.utc),
            )
            .count()
        )

        activities = []
        # Dynamic time allocation based on target_minutes (e.g., 20 mins)
        conv_mins = max(5, int(target_minutes * 0.45))
        test_mins = max(3, int(target_minutes * 0.25))
        vocab_mins = max(2, int(target_minutes * 0.15))
        mistake_mins = max(2, target_minutes - conv_mins - test_mins - vocab_mins)

        # Activity 1: AI Speaking
        topic = "Job Interview & Communication" if frequent_mistakes else "Everyday Fluency & Life"
        activities.append({
            "id": "act-1",
            "title": "Interactive Speaking Session",
            "type": "conversation",
            "target_minutes": conv_mins,
            "completed_minutes": 0,
            "is_completed": False,
            "description": f"Engage in spoken dialogue focused on {topic}.",
        })

        # Activity 2: Targeted Grammar
        grammar_focus = frequent_mistakes[0].category.replace("_", " ").title() if frequent_mistakes else "Tenses & Collocations"
        activities.append({
            "id": "act-2",
            "title": f"Targeted Test: {grammar_focus}",
            "type": "grammar",
            "target_minutes": test_mins,
            "completed_minutes": 0,
            "is_completed": False,
            "description": f"Targeted 5-10 question drill addressing {grammar_focus}.",
        })

        # Activity 3: Spaced Repetition Vocabulary
        activities.append({
            "id": "act-3",
            "title": "Vocabulary Flashcard Review",
            "type": "vocabulary",
            "target_minutes": vocab_mins,
            "completed_minutes": 0,
            "is_completed": False,
            "description": f"Revise {max(5, due_vocab_count)} priority vocabulary words using spaced repetition.",
        })

        # Activity 4: Error Notebook Revision
        if frequent_mistakes:
            activities.append({
                "id": "act-4",
                "title": "Mistake Memory Revision",
                "type": "mistakes",
                "target_minutes": mistake_mins,
                "completed_minutes": 0,
                "is_completed": False,
                "description": f"Review {len(frequent_mistakes)} active mistakes recorded from previous sessions.",
            })

        return {
            "plan_date": today_str,
            "target_minutes": target_minutes,
            "completed_minutes": 0,
            "is_completed": False,
            "activities": activities,
        }
