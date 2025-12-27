"""Routes FastAPI pour le comportement de l'apprenant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learner_behavior import LearnerBehavior
from app.models.learner import Learner
from app.schemas.learner_behavior import (
    LearnerBehaviorCreate,
    LearnerBehaviorResponse
)
from app.core.deps import get_db
from app.services.behavior_service import (
    compute_engagement,
    get_behavior_profile
)

router = APIRouter(prefix="/behavior", tags=["Learner Behavior"])


@router.post("/", response_model=LearnerBehaviorResponse)
def update_behavior(
    data: LearnerBehaviorCreate,
    db: Session = Depends(get_db)
):
    """Mettre à jour le profil comportemental d'un apprenant."""
    learner = db.query(Learner).get(data.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Calculer le score d'engagement
    engagement = compute_engagement(
        data.sessions_count,
        data.activities_count,
        data.total_time_spent
    )
    
    # Vérifier si un enregistrement existe déjà
    existing = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == data.learner_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.sessions_count = data.sessions_count
        existing.activities_count = data.activities_count
        existing.total_time_spent = data.total_time_spent
        existing.engagement_score = engagement
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Créer
        behavior = LearnerBehavior(
            **data.dict(),
            engagement_score=engagement
        )
        db.add(behavior)
        db.commit()
        db.refresh(behavior)
        return behavior


@router.get("/{learner_id}", response_model=LearnerBehaviorResponse)
def get_behavior(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer le profil comportemental d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    behavior = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == learner_id
    ).first()
    
    if not behavior:
        raise HTTPException(status_code=404, detail="Profil comportemental non trouvé")
    
    return behavior


@router.get("/profile/{learner_id}")
def get_behavior_profile_endpoint(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un profil comportemental détaillé."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    behavior = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == learner_id
    ).first()
    
    if not behavior:
        raise HTTPException(status_code=404, detail="Profil comportemental non trouvé")
    
    profile = get_behavior_profile(
        behavior.sessions_count,
        behavior.activities_count,
        behavior.total_time_spent
    )
    
    return profile
