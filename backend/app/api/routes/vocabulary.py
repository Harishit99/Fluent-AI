import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile
from app.models.vocabulary import VocabularyItem, VocabularyReview
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyOut,
    VocabularyReviewRequest,
    VocabularyReviewOut,
)
from app.services.adaptive_learning.engine import AdaptiveLearningEngine

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


def item_to_schema(item: VocabularyItem) -> VocabularyOut:
    syns = json.loads(item.synonyms_json) if item.synonyms_json else []
    ants = json.loads(item.antonyms_json) if item.antonyms_json else []
    rev_out = None
    if item.review:
        rev_out = VocabularyReviewOut(
            repetition_count=item.review.repetition_count,
            interval_days=item.review.interval_days,
            ease_factor=item.review.ease_factor,
            next_review_date=item.review.next_review_date,
        )

    return VocabularyOut(
        id=item.id,
        user_id=item.user_id,
        word=item.word,
        meaning=item.meaning,
        part_of_speech=item.part_of_speech,
        example_sentence=item.example_sentence,
        hindi_translation=item.hindi_translation,
        synonyms=syns,
        antonyms=ants,
        cefr_level=item.cefr_level,
        mastery_status=item.mastery_status,
        user_notes=item.user_notes,
        created_at=item.created_at,
        review=rev_out,
    )


@router.get("", response_model=List[VocabularyOut])
def list_vocabulary(
    search: Optional[str] = None,
    mastery_status: Optional[str] = None,
    cefr_level: Optional[str] = None,
    due_for_review: bool = False,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(VocabularyItem).filter(VocabularyItem.user_id == current_user.id)

    if search:
        query = query.filter(
            (VocabularyItem.word.ilike(f"%{search}%"))
            | (VocabularyItem.meaning.ilike(f"%{search}%"))
        )
    if mastery_status and mastery_status != "all":
        query = query.filter(VocabularyItem.mastery_status == mastery_status)
    if cefr_level and cefr_level != "all":
        query = query.filter(VocabularyItem.cefr_level == cefr_level)
    if due_for_review:
        query = query.join(VocabularyReview).filter(
            VocabularyReview.next_review_date <= datetime.now(timezone.utc)
        )

    items = query.order_by(VocabularyItem.created_at.desc()).limit(limit).all()
    return [item_to_schema(i) for i in items]


@router.post("", response_model=VocabularyOut)
def add_vocabulary(
    data: VocabularyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check duplicate word
    existing = (
        db.query(VocabularyItem)
        .filter(VocabularyItem.user_id == current_user.id, VocabularyItem.word.ilike(data.word.strip()))
        .first()
    )
    if existing:
        return item_to_schema(existing)

    item = VocabularyItem(
        user_id=current_user.id,
        word=data.word.strip(),
        meaning=data.meaning.strip(),
        part_of_speech=data.part_of_speech or "noun",
        example_sentence=data.example_sentence.strip(),
        hindi_translation=data.hindi_translation,
        synonyms_json=json.dumps(data.synonyms or []),
        antonyms_json=json.dumps(data.antonyms or []),
        cefr_level=data.cefr_level or "B1",
        mastery_status="learning",
        user_notes=data.user_notes,
    )
    db.add(item)
    db.flush()

    # Initialize SuperMemo review tracking
    review = VocabularyReview(
        item_id=item.id,
        repetition_count=0,
        interval_days=1,
        ease_factor=2.5,
        next_review_date=datetime.now(timezone.utc),
    )
    db.add(review)
    db.commit()
    db.refresh(item)

    return item_to_schema(item)


@router.patch("/{word_id}", response_model=VocabularyOut)
def update_vocabulary(
    word_id: str,
    data: VocabularyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(VocabularyItem)
        .filter(VocabularyItem.id == word_id, VocabularyItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary word not found.")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(item, field, val)

    db.commit()
    db.refresh(item)
    return item_to_schema(item)


@router.delete("/{word_id}")
def delete_vocabulary(
    word_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(VocabularyItem)
        .filter(VocabularyItem.id == word_id, VocabularyItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary word not found.")

    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": word_id}


@router.post("/review")
def review_vocabulary(
    data: VocabularyReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(VocabularyItem)
        .filter(VocabularyItem.id == data.word_id, VocabularyItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary word not found.")

    review = db.query(VocabularyReview).filter(VocabularyReview.item_id == item.id).first()
    if not review:
        review = VocabularyReview(item_id=item.id)
        db.add(review)

    # SuperMemo SM-2 calculation
    updated_srs = AdaptiveLearningEngine.calculate_srs_next_review(
        rating=data.rating,
        repetition_count=review.repetition_count,
        interval_days=review.interval_days,
        ease_factor=review.ease_factor,
    )

    review.repetition_count = updated_srs["repetition_count"]
    review.interval_days = updated_srs["interval_days"]
    review.ease_factor = updated_srs["ease_factor"]
    review.next_review_date = updated_srs["next_review_date"]
    review.last_reviewed_at = datetime.now(timezone.utc)

    # Update item status
    if review.repetition_count >= 4 and review.interval_days >= 14:
        item.mastery_status = "mastered"
    elif review.repetition_count >= 1:
        item.mastery_status = "reviewing"
    else:
        item.mastery_status = "learning"

    db.commit()
    return {
        "word_id": item.id,
        "word": item.word,
        "mastery_status": item.mastery_status,
        "interval_days": review.interval_days,
        "next_review_date": review.next_review_date,
    }
