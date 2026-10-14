from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile, LearningPreferences
from app.models.conversation import Conversation, ConversationMessage
from app.models.mistake import CorrectionRecord
from app.models.learning import SkillProgress
from app.schemas.conversation import (
    ConversationCreate,
    ConversationOut,
    MessageCreate,
    MessageOut,
    ConversationFinish,
    CorrectionItem,
)
from app.services.conversation.orchestrator import ConversationOrchestrator

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut)
def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(
        user_id=current_user.id,
        mode=data.mode,
        topic=data.topic,
        status="active",
    )
    db.add(conv)
    db.flush()

    # Generate introductory opening prompt from tutor based on mode
    openings = {
        "instant": f"Hello! I am your FluentUp English tutor. Today let's discuss '{data.topic}'. Whenever you speak, I'll gently highlight key corrections. To start, how would you describe your experience with this topic?",
        "natural": f"Hi there! Glad we're chatting today about '{data.topic}'. Let's just talk naturally. Tell me, what's been on your mind recently regarding this?",
        "fluency": f"Welcome to your Fluency Session! We're focusing on '{data.topic}'. Try giving detailed responses without worrying about small slips. Ready? Tell me your perspective on this topic.",
        "interview": f"Good day. Thank you for joining today's placement and interview preparation session. Today's scenario focuses on: '{data.topic}'. Could you begin by introducing yourself and sharing your relevant background?",
        "roleplay": f"Welcome! We are practicing a real-world scenario: '{data.topic}'. I will be your conversation partner. Let's begin! Hello, how can I help you today?",
        "free": f"Hello! I'm here to chat with you about '{data.topic}'. Feel free to type or tap the microphone to speak. What would you like to discuss first?",
    }
    intro = openings.get(data.mode, openings["free"])

    init_msg = ConversationMessage(
        conversation_id=conv.id,
        sender="assistant",
        content=intro,
    )
    db.add(init_msg)
    db.commit()
    db.refresh(conv)

    return conv


@router.get("", response_model=List[ConversationOut])
def list_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
        .limit(limit)
        .all()
    )
    return convs


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found.")
    return conv


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def post_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found.")

    # 1. Save user message
    user_msg = ConversationMessage(
        conversation_id=conv.id,
        sender="user",
        content=data.content,
        audio_url=data.audio_url,
    )
    db.add(user_msg)
    db.flush()

    # 2. Retrieve history for contextual awareness
    past_messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conv.id)
        .order_by(ConversationMessage.created_at.asc())
        .limit(10)
        .all()
    )
    history_dicts = [{"sender": m.sender, "content": m.content} for m in past_messages]

    # Get user preferences for explanation language
    prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
    lang = prefs.explanation_language if prefs else "en"

    # 3. Process turn via Orchestrator
    reply_text, raw_corrections = ConversationOrchestrator.process_turn(
        mode=conv.mode,
        topic=conv.topic,
        history=history_dicts,
        user_message=data.content,
        explanation_language=lang,
    )

    # 4. Save any detected grammar corrections to Mistake Notebook
    correction_items: List[CorrectionItem] = []
    for c in raw_corrections:
        # Check if already recorded previously
        existing = (
            db.query(CorrectionRecord)
            .filter(
                CorrectionRecord.user_id == current_user.id,
                CorrectionRecord.original_sentence == c["original"],
            )
            .first()
        )
        if existing:
            existing.occurrence_count += 1
            existing.last_practiced_at = datetime.now(timezone.utc)
            existing.mastery_status = "learning"
        else:
            rec = CorrectionRecord(
                user_id=current_user.id,
                conversation_id=conv.id,
                original_sentence=c["original"],
                corrected_sentence=c["corrected"],
                category=c.get("category", "grammar"),
                explanation=c.get("explanation", ""),
                natural_alternative=c.get("natural_alternative"),
                example_sentence=c.get("example_sentence"),
                severity=c.get("severity", "important"),
                practice_recommended=True,
            )
            db.add(rec)

        correction_items.append(CorrectionItem(
            original=c["original"],
            corrected=c["corrected"],
            category=c.get("category", "grammar"),
            explanation=c.get("explanation", ""),
            natural_alternative=c.get("natural_alternative"),
            severity=c.get("severity", "important"),
            practice_recommended=True,
        ))

    # 5. Save assistant reply
    assistant_msg = ConversationMessage(
        conversation_id=conv.id,
        sender="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Return message with attached inline corrections
    return MessageOut(
        id=assistant_msg.id,
        conversation_id=assistant_msg.conversation_id,
        sender=assistant_msg.sender,
        content=assistant_msg.content,
        audio_url=assistant_msg.audio_url,
        created_at=assistant_msg.created_at,
        corrections=correction_items,
    )


@router.post("/{conversation_id}/finish", response_model=ConversationOut)
def finish_conversation(
    conversation_id: str,
    data: ConversationFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found.")

    conv.status = "completed"
    conv.ended_at = datetime.now(timezone.utc)
    conv.summary = data.summary or (
        f"Completed {conv.mode.capitalize()} practice session on '{conv.topic}'. "
        "Demonstrated active communication and sentence formation."
    )

    # Increment profile practice minutes
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        profile.total_minutes_practiced += 10
        profile.last_active_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Update speaking skill progress
    sp = (
        db.query(SkillProgress)
        .filter(SkillProgress.user_id == current_user.id, SkillProgress.skill_name == "speaking")
        .first()
    )
    if sp:
        sp.total_attempts += 1
        sp.last_practiced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(conv)
    return conv
