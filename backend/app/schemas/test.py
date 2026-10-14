from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TestGenerateRequest(BaseModel):
    topic: str = Field("all", description="tenses, articles, prepositions, subject_verb_agreement, vocabulary, all, revision")
    cefr_level: str = Field("A2", description="A1, A2, B1, B2, C1, C2")
    question_count: int = Field(5, ge=1, le=50)
    test_mode: str = Field("quick_5", description="quick_5, standard_10, challenge_20, custom, revision")


class TestQuestionOut(BaseModel):
    id: str
    topic: str
    cefr_level: str
    question_type: str
    prompt: str
    options: List[str] = []


class QuestionAnswerItem(BaseModel):
    question_id: str
    user_answer: str


class TestSubmitRequest(BaseModel):
    time_taken_seconds: int = 0
    answers: List[QuestionAnswerItem]


class TestResponseResult(BaseModel):
    question_id: str
    prompt: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class TestSubmitResponse(BaseModel):
    attempt_id: str
    topic: str
    cefr_level: str
    total_questions: int
    correct_count: int
    score_percentage: float
    time_taken_seconds: int
    level_recommendation: Optional[str] = None
    results: List[TestResponseResult]


class TestAttemptOut(BaseModel):
    id: str
    topic: str
    cefr_level: str
    test_mode: str
    total_questions: int
    correct_count: int
    score_percentage: float
    time_taken_seconds: int
    completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestAttemptDetail(TestAttemptOut):
    responses: List[TestResponseResult] = []
