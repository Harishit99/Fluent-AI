from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, Profile, LearningPreferences
from app.models.learning import SkillProgress
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def init_user_defaults(db: Session, user: User, display_name: str = "English Learner"):
    profile = Profile(user_id=user.id, display_name=display_name, streak_count=1)
    db.add(profile)

    prefs = LearningPreferences(user_id=user.id, current_level="A2")
    db.add(prefs)

    skills = ["grammar", "vocabulary", "speaking", "listening", "pronunciation"]
    for s in skills:
        sp = SkillProgress(
            user_id=user.id,
            skill_name=s,
            estimated_level="A2",
            accuracy_percentage=65.0,
            total_attempts=0,
            confidence_score=0.2,
        )
        db.add(sp)


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    init_user_defaults(db, user, data.display_name or "English Learner")
    db.commit()

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        display_name=data.display_name or "English Learner",
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    display_name = user.profile.display_name if user.profile else "English Learner"
    token = create_access_token(data={"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        display_name=display_name,
    )


@router.post("/demo", response_model=TokenResponse)
def demo_access(db: Session = Depends(get_db)):
    """Provides instant guest/demo access for seamless evaluation."""
    demo_email = "demo.learner@fluentup.ai"
    user = db.query(User).filter(User.email == demo_email).first()

    if not user:
        user = User(
            email=demo_email,
            hashed_password=hash_password("DemoLearnerPass123!"),
        )
        db.add(user)
        db.flush()
        init_user_defaults(db, user, "Alex Johnson (Demo)")
        db.commit()

    display_name = user.profile.display_name if user.profile else "Alex Johnson (Demo)"
    token = create_access_token(data={"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        display_name=display_name,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    display_name = current_user.profile.display_name if current_user.profile else "English Learner"
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        display_name=display_name,
        created_at=current_user.created_at,
    )
