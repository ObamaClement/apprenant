"""Routes FastAPI pour le profil cognitif de l'apprenant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learner_cognitive import LearnerCognitiveProfile
from app.models.learner import Learner
from app.schemas.learner_cognitive import (
    LearnerCognitiveCreate,
    LearnerCognitiveResponse
)
from app.core.deps import get_db

router = APIRouter(prefix="/cognitive", tags=["Learner Cognitive"])


@router.post("/", response_model=LearnerCognitiveResponse)
def create_cognitive_profile(
    data: LearnerCognitiveCreate,
    db: Session = Depends(get_db)
):
    """Créer un profil cognitif pour un apprenant."""
    learner = db.query(Learner).get(data.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Vérifier si un profil existe déjà
    existing = db.query(LearnerCognitiveProfile).filter(
        LearnerCognitiveProfile.learner_id == data.learner_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Un profil cognitif existe déjà pour cet apprenant")
    
    profile = LearnerCognitiveProfile(**data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{learner_id}", response_model=LearnerCognitiveResponse)
def get_cognitive_profile(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer le profil cognitif d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    profile = db.query(LearnerCognitiveProfile).filter(
        LearnerCognitiveProfile.learner_id == learner_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil cognitif non trouvé")
    
    return profile


@router.put("/{learner_id}", response_model=LearnerCognitiveResponse)
def update_cognitive_profile(
    learner_id: int,
    data: LearnerCognitiveCreate,
    db: Session = Depends(get_db)
):
    """Mettre à jour le profil cognitif d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    profile = db.query(LearnerCognitiveProfile).filter(
        LearnerCognitiveProfile.learner_id == learner_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil cognitif non trouvé")
    
    profile.learning_style = data.learning_style
    profile.learning_speed = data.learning_speed
    profile.autonomy_level = data.autonomy_level
    
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{learner_id}")
def delete_cognitive_profile(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer le profil cognitif d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    profile = db.query(LearnerCognitiveProfile).filter(
        LearnerCognitiveProfile.learner_id == learner_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil cognitif non trouvé")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Profil cognitif supprimé avec succès"}
