from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VocabularyCreate(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    meaning: str = Field(..., min_length=1)
    part_of_speech: Optional[str] = "noun"
    example_sentence: str = Field(..., min_length=1)
    hindi_translation: Optional[str] = None
    synonyms: Optional[List[str]] = []
    antonyms: Optional[List[str]] = []
    cefr_level: Optional[str] = "B1"
    user_notes: Optional[str] = None


class VocabularyUpdate(BaseModel):
    meaning: Optional[str] = None
    part_of_speech: Optional[str] = None
    example_sentence: Optional[str] = None
    hindi_translation: Optional[str] = None
    mastery_status: Optional[str] = None  # learning, reviewing, mastered
    user_notes: Optional[str] = None


class VocabularyReviewOut(BaseModel):
    repetition_count: int
    interval_days: int
    ease_factor: float
    next_review_date: datetime


class VocabularyOut(BaseModel):
    id: str
    user_id: str
    word: str
    meaning: str
    part_of_speech: Optional[str] = None
    example_sentence: str
    hindi_translation: Optional[str] = None
    synonyms: List[str] = []
    antonyms: List[str] = []
    cefr_level: str
    mastery_status: str
    user_notes: Optional[str] = None
    created_at: datetime
    review: Optional[VocabularyReviewOut] = None

    class Config:
        from_attributes = True


class VocabularyReviewRequest(BaseModel):
    word_id: str
    rating: int = Field(..., ge=1, le=5, description="1 (forgot), 3 (hard/recalled), 5 (perfect/easy)")
