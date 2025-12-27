"""Routes FastAPI pour l'historique d'apprentissage."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learning_history import LearningHistory
from app.models.learner import Learner
from app.schemas.learning_history import (
    LearningHistoryCreate,
    LearningHistoryResponse
)
from app.core.deps import get_db

router = APIRouter(
    prefix="/learning-history",
    tags=["Learning History"]
)


@router.post("/", response_model=LearningHistoryResponse)
def create_history(
    history: LearningHistoryCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouvel enregistrement d'historique d'apprentissage."""
    learner = db.query(Learner).get(history.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    new_history = LearningHistory(**history.dict())
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


@router.get("/learner/{learner_id}", response_model=list[LearningHistoryResponse])
def get_learner_history(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer l'historique d'apprentissage d'un apprenant."""
    return (
        db.query(LearningHistory)
        .filter(LearningHistory.learner_id == learner_id)
        .order_by(LearningHistory.created_at.desc())
        .all()
    )
