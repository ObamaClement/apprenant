"""Routes FastAPI pour l'état affectif de l'apprenant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learner_affective import LearnerAffectiveState
from app.models.learner import Learner
from app.schemas.learner_affective import (
    LearnerAffectiveCreate,
    LearnerAffectiveResponse
)
from app.core.deps import get_db
from app.services.affective_service import (
    update_affective_state,
    get_affective_profile,
    get_feedback_type
)

router = APIRouter(prefix="/affective", tags=["Learner Affective"])


@router.post("/", response_model=LearnerAffectiveResponse)
def create_or_update_affective(
    data: LearnerAffectiveCreate,
    db: Session = Depends(get_db)
):
    """Créer ou mettre à jour l'état affectif d'un apprenant."""
    learner = db.query(Learner).get(data.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Vérifier si un enregistrement existe déjà
    existing = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == data.learner_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.motivation = data.motivation
        existing.frustration = data.frustration
        existing.confidence = data.confidence
        existing.stress = data.stress
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Créer
        affective = LearnerAffectiveState(**data.dict())
        db.add(affective)
        db.commit()
        db.refresh(affective)
        return affective


@router.get("/{learner_id}", response_model=LearnerAffectiveResponse)
def get_affective_state(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer l'état affectif d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    return affective


@router.post("/update-from-score/{learner_id}/{score}")
def update_from_score(
    learner_id: int,
    score: float,
    db: Session = Depends(get_db)
):
    """Mettre à jour l'état affectif basé sur un score de performance."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    if not 0 <= score <= 100:
        raise HTTPException(status_code=400, detail="Le score doit être entre 0 et 100")
    
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    if not affective:
        # Créer un nouvel enregistrement avec état initial
        affective = LearnerAffectiveState(learner_id=learner_id)
        db.add(affective)
        db.commit()
        db.refresh(affective)
    
    # Mettre à jour l'état affectif
    motivation, frustration, confidence, stress = update_affective_state(
        affective.motivation,
        affective.frustration,
        affective.confidence,
        affective.stress,
        score
    )
    
    affective.motivation = motivation
    affective.frustration = frustration
    affective.confidence = confidence
    affective.stress = stress
    
    db.commit()
    db.refresh(affective)
    
    return {
        "learner_id": learner_id,
        "score": score,
        "motivation": motivation,
        "frustration": frustration,
        "confidence": confidence,
        "stress": stress,
        "message": "État affectif mis à jour"
    }


@router.get("/profile/{learner_id}")
def get_affective_profile_endpoint(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un profil affectif détaillé."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    profile = get_affective_profile(
        affective.motivation,
        affective.frustration,
        affective.confidence,
        affective.stress
    )
    
    return profile


@router.get("/feedback-type/{learner_id}")
def get_feedback_type_endpoint(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir le type de feedback recommandé."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    feedback_type = get_feedback_type(
        affective.motivation,
        affective.frustration,
        affective.confidence,
        affective.stress
    )
    
    return {
        "learner_id": learner_id,
        "feedback_type": feedback_type,
        "description": _get_feedback_description(feedback_type)
    }


def _get_feedback_description(feedback_type: str) -> str:
    """Obtenir une description du type de feedback."""
    descriptions = {
        "encouragement": "Fournir des encouragements et renforcer la motivation",
        "aide": "Fournir une aide équilibrée avec guidance",
        "challenge": "Proposer des défis plus complexes",
        "soutien": "Fournir un soutien émotionnel et pédagogique"
    }
    return descriptions.get(feedback_type, "Type de feedback inconnu")
