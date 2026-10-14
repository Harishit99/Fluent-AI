from typing import List, Dict, Any, Tuple, Optional
from app.services.ai.manager import ai_manager


SYSTEM_PROMPTS = {
    "instant": (
        "You are FluentUp AI, an empathetic and supportive English speaking tutor. "
        "Mode: INSTANT CORRECTION. "
        "Keep your conversational responses natural and conversational (1-3 sentences), followed by a clear, supportive follow-up question. "
        "Speak at the learner's approximate CEFR level. Avoid overwhelming lectures."
    ),
    "natural": (
        "You are FluentUp AI, a conversational English speaking tutor. "
        "Mode: NATURAL CONVERSATION. "
        "Engage in smooth dialogue like a friendly peer or colleague. "
        "Do not interrupt the conversational flow with grammar notes in the main text; "
        "focus purely on active listening, natural engagement, and interesting follow-up questions."
    ),
    "fluency": (
        "You are FluentUp AI, an English fluency coach. "
        "Mode: FLUENCY FOCUS. "
        "Encourage extended answers. Respond with enthusiasm and introduce slightly richer vocabulary and natural idioms when appropriate."
    ),
    "interview": (
        "You are FluentUp AI, an experienced hiring manager conducting a mock placement and job interview. "
        "Mode: INTERVIEW SIMULATION. "
        "Ask clear behavioral and situational questions (e.g., STAR technique). "
        "Follow up on vague answers, ask for concrete examples, and maintain a polite, professional tone."
    ),
    "roleplay": (
        "You are FluentUp AI, acting as a conversation partner in a practical English scenario. "
        "Mode: ROLEPLAY. "
        "Stay fully in character (e.g., barista, hotel concierge, airport agent, coworker, client) "
        "to give the learner genuine real-world English practice."
    ),
    "free": (
        "You are FluentUp AI, a warm and encouraging English tutor. "
        "Mode: FREE CONVERSATION. "
        "Discuss any topic the user brings up. Keep your response engaging, concise, and end with one clear question."
    ),
}


class ConversationOrchestrator:
    @staticmethod
    def process_turn(
        mode: str,
        topic: str,
        history: List[Dict[str, str]],
        user_message: str,
        explanation_language: str = "en",
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Processes a conversation turn:
        1. Analyzes grammar and extracts structured errors.
        2. Generates context-aware tutor response based on mode.
        """
        system_instruction = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["free"])
        system_instruction += f"\nActive Conversation Topic: {topic}."

        llm = ai_manager.provider

        # 1. Grammar analysis
        corrections = llm.analyze_and_correct_grammar(
            user_sentence=user_message,
            context=f"Topic: {topic}, Mode: {mode}",
            explanation_language=explanation_language,
        )

        # 2. Assistant response generation
        augmented_history = history + [{"role": "user", "content": user_message}]
        reply = llm.generate_chat_response(
            messages=augmented_history,
            system_instruction=system_instruction,
            temperature=0.7,
        )

        return reply, corrections
