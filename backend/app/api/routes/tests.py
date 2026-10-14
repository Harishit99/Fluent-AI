import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile
from app.models.test import GrammarQuestion, TestAttempt, TestResponse
from app.models.mistake import CorrectionRecord
from app.models.learning import SkillProgress
from app.schemas.test import (
    TestGenerateRequest,
    TestQuestionOut,
    TestSubmitRequest,
    TestSubmitResponse,
    TestAttemptOut,
    TestAttemptDetail,
    TestResponseResult,
)
from app.services.assessment.question_bank import get_bank_questions
from app.services.assessment.scorer import evaluate_submission
from app.services.adaptive_learning.engine import AdaptiveLearningEngine
from app.services.ai.manager import ai_manager

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/generate", response_model=dict)
def generate_test(
    data: TestGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates a new test with NO artificial daily cap.
    Supports 5, 10, 20, or custom question count, and revision tests from mistake records.
    """
    q_count = data.question_count

    # 1. Revision Mode: generate questions directly from learner's recorded mistakes
    if data.topic == "revision" or data.test_mode == "revision":
        mistakes = (
            db.query(CorrectionRecord)
            .filter(CorrectionRecord.user_id == current_user.id, CorrectionRecord.mastery_status != "mastered")
            .limit(q_count)
            .all()
        )
        if mistakes:
            raw_questions = []
            for idx, m in enumerate(mistakes):
                raw_questions.append({
                    "id": f"rev-{m.id}",
                    "topic": m.category,
                    "cefr_level": data.cefr_level,
                    "question_type": "sentence_correction",
                    "prompt": f"Identify the error and correct: '{m.original_sentence}'",
                    "options": [
                        m.corrected_sentence,
                        m.original_sentence,
                        f"I {m.original_sentence}",
                        "None of the above",
                    ],
                    "correct_answer": m.corrected_sentence,
                    "explanation": m.explanation,
                })
        else:
            raw_questions = get_bank_questions(topic="all", cefr_level=data.cefr_level, count=q_count)
    else:
        # Standard or AI generated question retrieval
        raw_questions = get_bank_questions(topic=data.topic, cefr_level=data.cefr_level, count=q_count)

    # 2. Persist questions into database to ensure trusted scoring
    db_questions: List[GrammarQuestion] = []
    client_questions: List[TestQuestionOut] = []

    for q in raw_questions:
        db_q = GrammarQuestion(
            topic=q.get("topic", data.topic),
            cefr_level=q.get("cefr_level", data.cefr_level),
            question_type=q.get("question_type", "multiple_choice"),
            prompt=q["prompt"],
            options_json=json.dumps(q.get("options", [])),
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
        )
        db.add(db_q)
        db.flush()
        db_questions.append(db_q)

        client_questions.append(TestQuestionOut(
            id=db_q.id,
            topic=db_q.topic,
            cefr_level=db_q.cefr_level,
            question_type=db_q.question_type,
            prompt=db_q.prompt,
            options=q.get("options", []),
        ))

    # 3. Create active test attempt
    attempt = TestAttempt(
        user_id=current_user.id,
        topic=data.topic,
        cefr_level=data.cefr_level,
        test_mode=data.test_mode,
        total_questions=len(client_questions),
        completed=False,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "topic": attempt.topic,
        "cefr_level": attempt.cefr_level,
        "test_mode": attempt.test_mode,
        "total_questions": attempt.total_questions,
        "questions": [q.model_dump() for q in client_questions],
    }


@router.post("/{test_id}/submit", response_model=TestSubmitResponse)
def submit_test(
    test_id: str,
    data: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = (
        db.query(TestAttempt)
        .filter(TestAttempt.id == test_id, TestAttempt.user_id == current_user.id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Test attempt not found.")

    if attempt.completed:
        raise HTTPException(status_code=400, detail="This test attempt has already been submitted.")

    # Retrieve all associated questions from database
    q_ids = [a.question_id for a in data.answers]
    questions = db.query(GrammarQuestion).filter(GrammarQuestion.id.in_(q_ids)).all()
    questions_map = {q.id: q for q in questions}

    # Evaluate on trusted backend
    correct_count, percentage, results_list, recommendation = evaluate_submission(
        attempt=attempt,
        questions_map=questions_map,
        answers=data.answers,
        time_taken_seconds=data.time_taken_seconds,
    )

    # Save individual responses
    for res in results_list:
        resp_row = TestResponse(
            attempt_id=attempt.id,
            question_id=res["question_id"],
            question_prompt=res["prompt"],
            user_answer=res["user_answer"],
            correct_answer=res["correct_answer"],
            is_correct=res["is_correct"],
            explanation=res["explanation"],
        )
        db.add(resp_row)

    # Finalize attempt
    attempt.correct_count = correct_count
    attempt.score_percentage = percentage
    attempt.time_taken_seconds = data.time_taken_seconds
    attempt.completed = True
    attempt.completed_at = datetime.now(timezone.utc)

    # Update profile practice metrics
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        profile.total_minutes_practiced += max(2, data.time_taken_seconds // 60)
        profile.last_active_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Adaptive skill progression update
    skill_progress = (
        db.query(SkillProgress)
        .filter(SkillProgress.user_id == current_user.id, SkillProgress.skill_name == "grammar")
        .first()
    )
    if skill_progress:
        smoothed = AdaptiveLearningEngine.smooth_skill_update(
            current_level=skill_progress.estimated_level,
            current_accuracy=skill_progress.accuracy_percentage,
            total_attempts=skill_progress.total_attempts,
            latest_score=percentage,
        )
        skill_progress.estimated_level = smoothed["estimated_level"]
        skill_progress.accuracy_percentage = smoothed["accuracy_percentage"]
        skill_progress.total_attempts = smoothed["total_attempts"]
        skill_progress.confidence_score = smoothed["confidence_score"]
        skill_progress.last_practiced_at = datetime.now(timezone.utc)

    db.commit()

    return TestSubmitResponse(
        attempt_id=attempt.id,
        topic=attempt.topic,
        cefr_level=attempt.cefr_level,
        total_questions=attempt.total_questions,
        correct_count=correct_count,
        score_percentage=percentage,
        time_taken_seconds=data.time_taken_seconds,
        level_recommendation=recommendation,
        results=[TestResponseResult(**r) for r in results_list],
    )


@router.get("/history", response_model=List[TestAttemptOut])
def list_test_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempts = (
        db.query(TestAttempt)
        .filter(TestAttempt.user_id == current_user.id, TestAttempt.completed == True)
        .order_by(TestAttempt.completed_at.desc())
        .limit(limit)
        .all()
    )
    return attempts


@router.get("/{test_id}/results", response_model=TestAttemptDetail)
def get_test_results(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = (
        db.query(TestAttempt)
        .filter(TestAttempt.id == test_id, TestAttempt.user_id == current_user.id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Test attempt not found.")

    responses = (
        db.query(TestResponse)
        .filter(TestResponse.attempt_id == attempt.id)
        .all()
    )

    results_out = [
        TestResponseResult(
            question_id=r.question_id,
            prompt=r.question_prompt,
            user_answer=r.user_answer,
            correct_answer=r.correct_answer,
            is_correct=r.is_correct,
            explanation=r.explanation or "",
        )
        for r in responses
    ]

    return TestAttemptDetail(
        id=attempt.id,
        topic=attempt.topic,
        cefr_level=attempt.cefr_level,
        test_mode=attempt.test_mode,
        total_questions=attempt.total_questions,
        correct_count=attempt.correct_count,
        score_percentage=attempt.score_percentage,
        time_taken_seconds=attempt.time_taken_seconds,
        completed=attempt.completed,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        responses=results_out,
    )
