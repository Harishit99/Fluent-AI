from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.mistake import CorrectionRecord
from app.schemas.mistake import CorrectionOut, CorrectionUpdate, CorrectionPracticeRequest

router = APIRouter(prefix="/mistakes", tags=["mistakes"])


@router.get("", response_model=List[CorrectionOut])
def list_mistakes(
    category: Optional[str] = None,
    mastery_status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(CorrectionRecord).filter(CorrectionRecord.user_id == current_user.id)

    if category and category != "all":
        query = query.filter(CorrectionRecord.category == category)
    if mastery_status and mastery_status != "all":
        query = query.filter(CorrectionRecord.mastery_status == mastery_status)
    if search:
        query = query.filter(
            (CorrectionRecord.original_sentence.ilike(f"%{search}%"))
            | (CorrectionRecord.corrected_sentence.ilike(f"%{search}%"))
            | (CorrectionRecord.explanation.ilike(f"%{search}%"))
        )

    records = query.order_by(CorrectionRecord.occurrence_count.desc(), CorrectionRecord.last_practiced_at.desc()).limit(limit).all()
    return records


@router.get("/{mistake_id}", response_model=CorrectionOut)
def get_mistake(
    mistake_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(CorrectionRecord)
        .filter(CorrectionRecord.id == mistake_id, CorrectionRecord.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Mistake record not found.")
    return record


@router.patch("/{mistake_id}", response_model=CorrectionOut)
def update_mistake(
    mistake_id: str,
    data: CorrectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(CorrectionRecord)
        .filter(CorrectionRecord.id == mistake_id, CorrectionRecord.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Mistake record not found.")

    if data.mastery_status is not None:
        record.mastery_status = data.mastery_status
    if data.practice_recommended is not None:
        record.practice_recommended = data.practice_recommended

    db.commit()
    db.refresh(record)
    return record


@router.post("/{mistake_id}/practice")
def practice_mistake(
    mistake_id: str,
    data: CorrectionPracticeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(CorrectionRecord)
        .filter(CorrectionRecord.id == mistake_id, CorrectionRecord.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Mistake record not found.")

    user_attempt = data.user_repetition_sentence.strip().lower()
    correct_form = record.corrected_sentence.strip().lower()

    # Check match or key correction inclusion
    is_accurate = correct_form in user_attempt or user_attempt in correct_form

    record.repetition_revisions += 1
    record.last_practiced_at = datetime.now(timezone.utc)

    if is_accurate:
        if record.repetition_revisions >= 2:
            record.mastery_status = "mastered"
        else:
            record.mastery_status = "understood"
        feedback = "Excellent! You used the correct phrasing accurately."
    else:
        record.mastery_status = "learning"
        feedback = f"Close attempt! Remember the target form: '{record.corrected_sentence}'."

    db.commit()
    return {
        "is_accurate": is_accurate,
        "mastery_status": record.mastery_status,
        "feedback": feedback,
        "target_form": record.corrected_sentence,
    }


@router.delete("/{mistake_id}")
def delete_mistake(
    mistake_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(CorrectionRecord)
        .filter(CorrectionRecord.id == mistake_id, CorrectionRecord.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Mistake record not found.")

    db.delete(record)
    db.commit()
    return {"status": "deleted", "id": mistake_id}
