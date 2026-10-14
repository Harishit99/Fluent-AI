from typing import List, Optional
from pydantic import BaseModel


class STTResponse(BaseModel):
    transcript: str
    confidence: float
    provider: str


class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    voice: Optional[str] = None


class TTSResponse(BaseModel):
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    provider: str


class PronunciationAnalysisRequest(BaseModel):
    target_sentence: str
    spoken_sentence: str
    audio_duration_seconds: Optional[float] = None


class WordStressFeedback(BaseModel):
    word: str
    match_status: str  # correct, missed, substituted
    feedback: str


class PronunciationAnalysisResponse(BaseModel):
    comprehensibility_score: float  # 0 to 100
    fluency_score: float  # 0 to 100
    phonemic_clarity_note: str
    word_feedback: List[WordStressFeedback]
    is_approximate: bool = True
    disclaimer: str = (
        "Pronunciation feedback is an approximate acoustic and comprehensibility assessment. "
        "It aims for clear, natural communication rather than accent elimination."
    )
