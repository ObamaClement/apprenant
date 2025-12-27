"""Routes FastAPI pour les performances de l'apprenant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learner_performance import LearnerPerformance
from app.models.learner import Learner
from app.models.concept import Concept
from app.schemas.learner_performance import (
    LearnerPerformanceCreate,
    LearnerPerformanceResponse
)
from app.core.deps import get_db
from app.services.performance_service import (
    get_learner_performance_stats,
    get_concept_performance_summary,
    identify_weak_concepts
)

router = APIRouter(
    prefix="/performances",
    tags=["Learner Performance"]
)


@router.post("/", response_model=LearnerPerformanceResponse)
def record_performance(
    data: LearnerPerformanceCreate,
    db: Session = Depends(get_db)
):
    """Enregistrer une performance d'apprenant."""
    # Vérifier que l'apprenant existe
    learner = db.query(Learner).get(data.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Vérifier que le concept existe
    concept = db.query(Concept).get(data.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    performance = LearnerPerformance(**data.dict())
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance


@router.get("/learner/{learner_id}", response_model=list[LearnerPerformanceResponse])
def get_learner_performances(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les performances d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return db.query(LearnerPerformance).filter(
        LearnerPerformance.learner_id == learner_id
    ).order_by(LearnerPerformance.created_at.desc()).all()


@router.get("/learner/{learner_id}/concept/{concept_id}", response_model=list[LearnerPerformanceResponse])
def get_learner_performances_for_concept(
    learner_id: int,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les performances d'un apprenant pour un concept spécifique."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    concept = db.query(Concept).get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    return db.query(LearnerPerformance).filter(
        LearnerPerformance.learner_id == learner_id,
        LearnerPerformance.concept_id == concept_id
    ).order_by(LearnerPerformance.created_at.desc()).all()


@router.get("/stats/{learner_id}")
def get_performance_stats(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de performance d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_learner_performance_stats(db, learner_id)


@router.get("/stats/{learner_id}/concept/{concept_id}")
def get_performance_stats_for_concept(
    learner_id: int,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de performance pour un concept spécifique."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    concept = db.query(Concept).get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    return get_learner_performance_stats(db, learner_id, concept_id)


@router.get("/summary/{learner_id}")
def get_performance_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un résumé des performances par concept."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_concept_performance_summary(db, learner_id)


@router.get("/weak-concepts/{learner_id}")
def get_weak_concepts(
    learner_id: int,
    threshold: float = 60.0,
    db: Session = Depends(get_db)
):
    """Identifier les concepts où l'apprenant a des difficultés."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    weak_concepts = identify_weak_concepts(db, learner_id, threshold)
    
    return {
        "learner_id": learner_id,
        "threshold": threshold,
        "weak_concepts_count": len(weak_concepts),
        "weak_concepts": weak_concepts
    }
