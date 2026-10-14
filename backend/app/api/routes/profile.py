from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Profile, LearningPreferences
from app.schemas.profile import ProfileOut, ProfileUpdate, PreferencesOut, PreferencesUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, display_name="English Learner")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.patch("", response_model=ProfileOut)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if data.display_name is not None:
        profile.display_name = data.display_name
    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url
    if data.bio is not None:
        profile.bio = data.bio

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/preferences", response_model=PreferencesOut)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
    if not prefs:
        prefs = LearningPreferences(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.patch("/preferences", response_model=PreferencesOut)
def update_preferences(
    data: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.query(LearningPreferences).filter(LearningPreferences.user_id == current_user.id).first()
    if not prefs:
        prefs = LearningPreferences(user_id=current_user.id)
        db.add(prefs)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(prefs, field, val)

    db.commit()
    db.refresh(prefs)
    return prefs
