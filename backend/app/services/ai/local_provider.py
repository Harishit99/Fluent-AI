import json
import re
from typing import List, Dict, Any, Optional
from app.services.ai.base import LLMProvider


class DeterministicLocalProvider(LLMProvider):
    """
    High-quality deterministic pedagogical engine.
    Ensures full offline & test functionality when external API keys are not supplied.
    """

    GRAMMAR_RULES = [
        {
            "pattern": r"\b(he|she|it)\s+don't\b",
            "replacement": r"\1 doesn't",
            "category": "subject_verb_agreement",
            "explanation": "Use 'doesn't' (does not) with third-person singular subjects (he, she, it) in the simple present tense.",
            "natural_alt": "He doesn't like that.",
            "example": "She doesn't eat spicy food.",
            "severity": "important",
        },
        {
            "pattern": r"\byesterday\s+i\s+go\b",
            "replacement": "yesterday I went",
            "category": "verb_tense",
            "explanation": "'Go' is irregular. Use the past tense 'went' when describing completed actions in the past.",
            "natural_alt": "Yesterday I went to college.",
            "example": "Yesterday I went to the market and met my friends.",
            "severity": "important",
        },
        {
            "pattern": r"\bi\s+didn't\s+went\b",
            "replacement": "I didn't go",
            "category": "verb_tense",
            "explanation": "After auxiliary 'did / didn't', always use the base form of the verb ('go', not 'went').",
            "natural_alt": "I didn't go there yesterday.",
            "example": "I didn't see him at the party.",
            "severity": "important",
        },
        {
            "pattern": r"\bi\s+am\s+engineer\b",
            "replacement": "I am an engineer",
            "category": "articles",
            "explanation": "Singular countable professions require indefinite articles ('a' or 'an'). Use 'an' before vowel sounds.",
            "natural_alt": "I work as a software engineer.",
            "example": "She is an architect.",
            "severity": "important",
        },
        {
            "pattern": r"\blisten\s+music\b",
            "replacement": "listen to music",
            "category": "prepositions",
            "explanation": "The verb 'listen' requires the preposition 'to' when followed by an object.",
            "natural_alt": "I like listening to music in my free time.",
            "example": "Please listen to the instructions carefully.",
            "severity": "important",
        },
        {
            "pattern": r"\bdiscuss\s+about\b",
            "replacement": "discuss",
            "category": "prepositions",
            "explanation": "'Discuss' is a transitive verb that directly takes an object. Do not add 'about'.",
            "natural_alt": "Let's discuss this topic tomorrow.",
            "example": "We discussed the project requirements in the meeting.",
            "severity": "important",
        },
        {
            "pattern": r"\bone\s+of\s+my\s+friend\b",
            "replacement": "one of my friends",
            "category": "singular_plural",
            "explanation": "The phrase 'one of...' refers to a single individual from a group, so the noun following must be plural ('friends').",
            "natural_alt": "One of my friends is visiting from Delhi.",
            "example": "One of my colleagues gave a presentation.",
            "severity": "important",
        },
        {
            "pattern": r"\bi\s+have\s+seen\s+him\s+yesterday\b",
            "replacement": "I saw him yesterday",
            "category": "verb_tense",
            "explanation": "Do not use the present perfect ('have seen') with specific past time indicators like 'yesterday' or 'last week'. Use simple past ('saw').",
            "natural_alt": "I saw him yesterday at the cafe.",
            "example": "I visited London two years ago.",
            "severity": "important",
        },
    ]

    HINGLISH_MAP = {
        "mujhe kal college jana hai": {
            "english": "I have to go to college tomorrow.",
            "explanation": "'Have to' expresses necessity or obligation. 'Tomorrow' refers to a future time.",
            "alternatives": ["I need to attend college tomorrow.", "I must go to college tomorrow."],
            "breakdown": [
                {"part": "Mujhe jana hai", "meaning": "I have to go"},
                {"part": "kal", "meaning": "tomorrow"},
                {"part": "college", "meaning": "to college"},
            ],
        },
        "main late ho gaya": {
            "english": "I got late / I am running late.",
            "explanation": "In English, use 'I got late' for a past delay, or 'I'm running late' if you are currently delayed.",
            "alternatives": ["I was delayed.", "Sorry, I am late."],
            "breakdown": [
                {"part": "Main ho gaya", "meaning": "I became / I got"},
                {"part": "late", "meaning": "delayed"},
            ],
        },
        "kya aap meri madad kar sakte hain": {
            "english": "Could you please help me?",
            "explanation": "'Could you please...' is a polite and professional way to request assistance.",
            "alternatives": ["Can you give me a hand?", "Would you mind helping me?"],
            "breakdown": [
                {"part": "Kya aap kar sakte hain", "meaning": "Could you please"},
                {"part": "meri madad", "meaning": "help me"},
            ],
        },
    }

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float = 0.7,
    ) -> str:
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user" or m.get("sender") == "user":
                last_user_msg = m.get("content", "").strip()
                break

        low = last_user_msg.lower()

        # Context-aware deterministic conversation responses
        if any(greet in low for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
            return (
                "Hello! Great to practice with you today. How has your day been so far? "
                "Tell me one interesting thing you did today."
            )
        elif "interview" in system_instruction.lower():
            if "tell me about yourself" in low or len(messages) <= 2:
                return (
                    "Thank you for joining today's practice interview. Let's start with a classic: "
                    "Could you walk me through your background and what you're currently working on?"
                )
            else:
                return (
                    "That sounds very insightful. When working on challenging projects, how do you usually prioritize your tasks under tight deadlines?"
                )
        elif "roleplay" in system_instruction.lower():
            return (
                "Welcome to the cafe! I'd be happy to take your order today. "
                "Would you like something hot to drink, or perhaps something from our bakery?"
            )
        elif "weekend" in low or "yesterday" in low or "went" in low or "did" in low:
            return (
                "That sounds wonderful! Who did you spend that time with, and did you learn anything new or encounter any surprises?"
            )
        elif "?" in last_user_msg:
            return (
                "That's a very thoughtful question. In professional English, asking clear questions demonstrates active listening. "
                "What made you think of that specifically?"
            )
        else:
            return (
                f"I understand what you mean regarding '{last_user_msg[:40]}...'. "
                "Could you expand on that with one more detail or an example from your personal experience?"
            )

    def analyze_and_correct_grammar(
        self,
        user_sentence: str,
        context: Optional[str] = None,
        explanation_language: str = "en",
    ) -> List[Dict[str, Any]]:
        corrections = []
        low = user_sentence.lower().strip()

        for rule in self.GRAMMAR_RULES:
            match = re.search(rule["pattern"], low, re.IGNORECASE)
            if match:
                # Construct corrected sentence
                corrected = re.sub(rule["pattern"], rule["replacement"], user_sentence, flags=re.IGNORECASE)
                explanation = rule["explanation"]
                if explanation_language == "hi":
                    explanation += " (हिंदी स्पष्टीकरण: हमेशा सही काल और सहायक क्रिया का प्रयोग करें।)"

                corrections.append({
                    "original": match.group(0),
                    "corrected": re.sub(rule["pattern"], rule["replacement"], match.group(0), flags=re.IGNORECASE),
                    "category": rule["category"],
                    "explanation": explanation,
                    "natural_alternative": rule["natural_alt"],
                    "example_sentence": rule["example"],
                    "severity": rule["severity"],
                    "practice_recommended": True,
                })

        return corrections

    def generate_practice_questions(
        self,
        topic: str,
        cefr_level: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        from app.services.assessment.question_bank import get_bank_questions
        return get_bank_questions(topic=topic, cefr_level=cefr_level, count=count)

    def translate_and_explain_hinglish(
        self,
        hinglish_sentence: str,
    ) -> Dict[str, Any]:
        norm = hinglish_sentence.strip().lower()
        if norm in self.HINGLISH_MAP:
            return self.HINGLISH_MAP[norm]

        # Generic intelligent response
        return {
            "english": f"English expression for: '{hinglish_sentence}'",
            "explanation": "To convey this naturally in English, express the action directly using appropriate tense and subject.",
            "alternatives": ["Try expressing this thought using simple Subject + Verb + Object structure."],
            "breakdown": [],
        }
