import json
import logging
from typing import List, Dict, Any, Optional
from app.services.ai.base import LLMProvider

logger = logging.getLogger("fluentup.openai")


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI Client: {e}")

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float = 0.7,
    ) -> str:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized or OPENAI_API_KEY missing.")

        formatted_msgs = [{"role": "system", "content": system_instruction}]
        for m in messages:
            role = m.get("role", m.get("sender", "user"))
            if role == "assistant" or role == "system":
                formatted_msgs.append({"role": role, "content": m.get("content", "")})
            else:
                formatted_msgs.append({"role": "user", "content": m.get("content", "")})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_msgs,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generate_chat_response error: {e}")
            raise

    def analyze_and_correct_grammar(
        self,
        user_sentence: str,
        context: Optional[str] = None,
        explanation_language: str = "en",
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        prompt = f"""
You are an expert English tutor for second-language learners.
Analyze the following sentence:
Sentence: "{user_sentence}"
Context: "{context or 'General conversation'}"
Explanation Language: "{explanation_language}"

Find any grammatical mistakes. If grammatically sound, return [].
Return ONLY valid JSON array with schema:
[
  {{
    "original": "error part",
    "corrected": "corrected part",
    "category": "verb_tense | subject_verb_agreement | articles | prepositions | word_order | natural_phrasing",
    "explanation": "concise explanation",
    "natural_alternative": "more natural phrase or null",
    "example_sentence": "example sentence",
    "severity": "minor | important | critical",
    "practice_recommended": true
  }}
]
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            logger.warning(f"OpenAI grammar error: {e}")
            return []

    def generate_practice_questions(
        self,
        topic: str,
        cefr_level: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        prompt = f"""
Generate {count} multiple-choice English grammar practice questions.
Topic: {topic}
CEFR Level: {cefr_level}

Return ONLY valid JSON array:
[
  {{
    "topic": "{topic}",
    "cefr_level": "{cefr_level}",
    "question_type": "multiple_choice",
    "prompt": "question prompt",
    "options": ["opt1", "opt2", "opt3", "opt4"],
    "correct_answer": "correct opt",
    "explanation": "educational explanation"
  }}
]
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            logger.warning(f"OpenAI question gen error: {e}")
            return []

    def translate_and_explain_hinglish(
        self,
        hinglish_sentence: str,
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        prompt = f"""
Learner sentence in Hindi/Hinglish: "{hinglish_sentence}"
Convert into natural English and explain.
Return JSON:
{{
  "english": "natural English",
  "explanation": "explanation",
  "alternatives": ["alt1"],
  "breakdown": []
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            logger.warning(f"OpenAI Hinglish error: {e}")
            return {"english": hinglish_sentence, "explanation": "Unavailable", "alternatives": [], "breakdown": []}
