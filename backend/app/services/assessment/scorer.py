from typing import List, Dict, Any, Tuple
from app.models.test import GrammarQuestion, TestAttempt, TestResponse
from app.schemas.test import QuestionAnswerItem, TestResponseResult, TestSubmitResponse


def evaluate_submission(
    attempt: TestAttempt,
    questions_map: Dict[str, GrammarQuestion],
    answers: List[QuestionAnswerItem],
    time_taken_seconds: int,
) -> Tuple[int, float, List[Dict[str, Any]], str]:
    """
    Trusted backend evaluation of learner answers.
    Guarantees no browser-tampered scores can compromise user records.
    """
    correct_count = 0
    results = []

    for ans in answers:
        q = questions_map.get(ans.question_id)
        if not q:
            continue

        clean_user = ans.user_answer.strip().lower()
        clean_correct = q.correct_answer.strip().lower()

        is_correct = clean_user == clean_correct
        if is_correct:
            correct_count += 1

        results.append({
            "question_id": q.id,
            "prompt": q.prompt,
            "user_answer": ans.user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    total = len(results) if results else 1
    percentage = round((correct_count / total) * 100, 1)

    # Adaptive recommendation based on demonstrated mastery
    if percentage >= 90.0:
        recommendation = "Outstanding mastery! You are ready to advance to higher complexity challenges."
    elif percentage >= 75.0:
        recommendation = "Strong performance. Review the explanations for the missed questions and practice variations."
    elif percentage >= 60.0:
        recommendation = "Moderate understanding. Focused repetition on this specific topic is recommended."
    else:
        recommendation = "Foundational reinforcement needed. Review grammar explanations and practice with 5-question bite-sized tests."

    return correct_count, percentage, results, recommendation
