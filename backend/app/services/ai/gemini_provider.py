import json
import logging
from typing import List, Dict, Any, Optional
from app.services.ai.base import LLMProvider

logger = logging.getLogger("fluentup.gemini")


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Could not initialize Google GenAI Client: {e}")

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float = 0.7,
    ) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized or GEMINI_API_KEY missing.")

        prompt_parts = [f"System Instruction:\n{system_instruction}\n\nChat History:"]
        for m in messages:
            role = m.get("role", m.get("sender", "user"))
            content = m.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")
        prompt_parts.append("Assistant:")
        full_prompt = "\n".join(prompt_parts)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generate_chat_response error: {e}")
            raise

    def analyze_and_correct_grammar(
        self,
        user_sentence: str,
        context: Optional[str] = None,
        explanation_language: str = "en",
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        prompt = f"""
You are an expert English tutor for second-language learners.
Analyze the following sentence spoken by an English learner:
Sentence: "{user_sentence}"
Context: "{context or 'General conversation'}"
Explanation Language: "{explanation_language}" (if 'hi', provide explanations with Hindi support).

Find any grammatical mistakes (tense, subject-verb agreement, articles, prepositions, word order, natural phrasing).
If the sentence is grammatically correct and natural, return an empty JSON array: [].

Return ONLY a valid JSON array of objects with the following schema:
[
  {{
    "original": "the exact wrong part or phrase",
    "corrected": "the corrected part or phrase",
    "category": "verb_tense | subject_verb_agreement | articles | prepositions | word_order | singular_plural | natural_phrasing",
    "explanation": "concise, warm, pedagogical explanation",
    "natural_alternative": "a more natural way native speakers would say this, or null",
    "example_sentence": "a clear example sentence using the correct form",
    "severity": "minor | important | critical",
    "practice_recommended": true
  }}
]
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            raw = response.text.strip()
            # Clean possible markdown fence
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Gemini grammar parsing error: {e}")
            return []

    def generate_practice_questions(
        self,
        topic: str,
        cefr_level: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        prompt = f"""
Generate {count} distinct English grammar practice questions.
Topic: {topic}
CEFR Level: {cefr_level}

Requirements:
- Multiple-choice format with 4 distinct options.
- Exactly one unequivocally correct answer.
- Plausible distractors based on common learner mistakes.
- Clear, educational explanation.

Return ONLY a valid JSON array matching this exact format:
[
  {{
    "topic": "{topic}",
    "cefr_level": "{cefr_level}",
    "question_type": "multiple_choice",
    "prompt": "Complete the sentence: She ____ to the library every Friday.",
    "options": ["go", "goes", "gone", "going"],
    "correct_answer": "goes",
    "explanation": "'She' is third-person singular, which takes 'goes' in simple present."
  }}
]
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Gemini question generation error: {e}")
            return []

    def translate_and_explain_hinglish(
        self,
        hinglish_sentence: str,
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        prompt = f"""
The learner spoke in Hindi or Hinglish: "{hinglish_sentence}"
Convert this into natural spoken English and explain the construction clearly.

Return ONLY a valid JSON object:
{{
  "english": "Natural English sentence",
  "explanation": "Clear explanation of grammar and word choice",
  "alternatives": ["alternative 1", "alternative 2"],
  "breakdown": [
    {{"part": "phrase", "meaning": "meaning"}}
  ]
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Gemini Hinglish error: {e}")
            return {
                "english": hinglish_sentence,
                "explanation": "Translation unavailable at this moment.",
                "alternatives": [],
                "breakdown": [],
            }
