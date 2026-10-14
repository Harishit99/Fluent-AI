from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.speech import PronunciationAnalysisRequest, PronunciationAnalysisResponse
from app.services.speech.service import speech_service
from app.core.config import settings

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/pronunciation", response_model=PronunciationAnalysisResponse)
def analyze_pronunciation(
    data: PronunciationAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluates learner spoken sentence against target text.
    Provides comprehensibility score, fluency rhythm, and word stress feedback.
    """
    return speech_service.analyze_pronunciation(
        target_sentence=data.target_sentence,
        spoken_sentence=data.spoken_sentence,
        audio_duration_seconds=data.audio_duration_seconds,
    )


@router.get("/status")
def speech_status():
    return {
        "stt_provider": settings.STT_PROVIDER,
        "tts_provider": settings.TTS_PROVIDER,
        "browser_speech_supported": True,
        "note": "Web Speech API is supported out-of-the-box in all modern browsers (Chrome, Edge, Safari, Firefox).",
    }
