import logging
from typing import Tuple, Dict, Any, Optional
from app.core.config import settings
from app.services.ai.base import LLMProvider
from app.services.ai.local_provider import DeterministicLocalProvider

logger = logging.getLogger("fluentup.ai_manager")


class ProviderManager:
    _instance: Optional["ProviderManager"] = None

    def __init__(self):
        self._provider: LLMProvider = DeterministicLocalProvider()
        self._provider_name: str = "local"
        self._is_live_api: bool = False
        self._status_note: str = "Deterministic Local Tutor Engine active (zero external API keys required)."
        self._initialize_provider()

    def _initialize_provider(self):
        pref = settings.LLM_PROVIDER.lower().strip()

        if pref == "gemini" and settings.GEMINI_API_KEY:
            try:
                from app.services.ai.gemini_provider import GeminiProvider
                self._provider = GeminiProvider(
                    api_key=settings.GEMINI_API_KEY,
                    model_name=settings.GEMINI_MODEL,
                )
                self._provider_name = "gemini"
                self._is_live_api = True
                self._status_note = f"Google Gemini API active ({settings.GEMINI_MODEL})."
                logger.info(self._status_note)
                return
            except Exception as e:
                logger.warning(f"Failed to load GeminiProvider, falling back to Local Tutor: {e}")

        elif pref == "openai" and settings.OPENAI_API_KEY:
            try:
                from app.services.ai.openai_provider import OpenAIProvider
                self._provider = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    model_name=settings.OPENAI_MODEL,
                )
                self._provider_name = "openai"
                self._is_live_api = True
                self._status_note = f"OpenAI API active ({settings.OPENAI_MODEL})."
                logger.info(self._status_note)
                return
            except Exception as e:
                logger.warning(f"Failed to load OpenAIProvider, falling back to Local Tutor: {e}")

        # Fallback to deterministic local tutor
        self._provider = DeterministicLocalProvider()
        self._provider_name = "local_tutor"
        self._is_live_api = False
        self._status_note = (
            "Local Tutor Engine active. To enable live Gemini or OpenAI generation, "
            "provide GEMINI_API_KEY or OPENAI_API_KEY in backend/.env."
        )
        logger.info(self._status_note)

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    def get_status(self) -> Dict[str, Any]:
        return {
            "configured_provider": settings.LLM_PROVIDER,
            "active_provider": self._provider_name,
            "is_live_api": self._is_live_api,
            "status_note": self._status_note,
        }


ai_manager = ProviderManager()
