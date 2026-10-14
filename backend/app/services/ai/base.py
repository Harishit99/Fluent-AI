from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    @abstractmethod
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float = 0.7,
    ) -> str:
        """Generate conversational response given chat history."""
        pass

    @abstractmethod
    def analyze_and_correct_grammar(
        self,
        user_sentence: str,
        context: Optional[str] = None,
        explanation_language: str = "en",
    ) -> List[Dict[str, Any]]:
        """Analyze sentence, extract errors, return structured corrections."""
        pass

    @abstractmethod
    def generate_practice_questions(
        self,
        topic: str,
        cefr_level: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        """Generate pedagogical multiple-choice / fill-blank questions."""
        pass

    @abstractmethod
    def translate_and_explain_hinglish(
        self,
        hinglish_sentence: str,
    ) -> Dict[str, Any]:
        """Convert Hindi/Hinglish sentence to natural English with explanation."""
        pass
