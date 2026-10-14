from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.services.ai.manager import ai_manager

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "app": "FluentUp AI", "version": "1.0.0"}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database_error": str(e)}


@router.get("/api/v1/status")
def system_status():
    ai_status = ai_manager.get_status()
    return {
        "status": "operational",
        "ai": ai_status,
        "features": {
            "unlimited_grammar_practice": True,
            "trusted_backend_scoring": True,
            "mistake_memory": True,
            "spaced_repetition": True,
            "speech_recognition": True,
            "tts_speech": True,
            "hinglish_translation": True,
        },
    }
