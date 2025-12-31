"""Routes FastAPI pour l'analyse des performances."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.learner import Learner
from app.services.performance_service import (
    get_learner_performance_stats,
    get_performance_by_difficulty,
    identify_weak_cases,
    get_performance_summary
)

router = APIRouter(prefix="/performances", tags=["Performance Analytics"])


@router.get("/stats/{learner_id}")
def get_stats(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de performance d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_learner_performance_stats(db, learner_id)


@router.get("/by-difficulty/{learner_id}")
def get_by_difficulty(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les performances par niveau de difficulté."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    stats = get_performance_by_difficulty(db, learner_id)
    
    return {
        "learner_id": learner_id,
        "by_difficulty": stats
    }


@router.get("/weak-cases/{learner_id}")
def get_weak_cases(
    learner_id: int,
    threshold: float = Query(60.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db)
):
    """Identifier les cas où l'apprenant a eu des difficultés."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    weak = identify_weak_cases(db, learner_id, threshold)
    
    return {
        "learner_id": learner_id,
        "threshold": threshold,
        "weak_cases_count": len(weak),
        "weak_cases": weak
    }


@router.get("/summary/{learner_id}")
def get_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un résumé complet des performances avec recommandations."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_performance_summary(db, learner_id)


@router.get("/trend/{learner_id}")
def get_trend(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir la tendance des performances."""
    from app.services.performance_service import compute_trend
    from app.models.simulation_session import SimulationSession
    
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id,
        SimulationSession.statut == "termine"
    ).order_by(SimulationSession.start_time).all()
    
    scores = [s.score_final for s in sessions if s.score_final is not None]
    
    if not scores:
        return {
            "learner_id": learner_id,
            "trend": "no_data",
            "message": "Pas assez de données pour calculer la tendance"
        }
    
    trend = compute_trend(scores)
    
    return {
        "learner_id": learner_id,
        "trend": trend,
        "nb_sessions": len(scores),
        "latest_scores": scores[-5:] if len(scores) >= 5 else scores,
        "message": _get_trend_message(trend)
    }


def _get_trend_message(trend: str) -> str:
    """Obtenir un message descriptif pour la tendance."""
    messages = {
        "improving": "Progression positive ! Continuez ainsi.",
        "stable": "Performance stable. Maintenir le rythme.",
        "declining": "Tendance à la baisse. Revoir les fondamentaux recommandé."
    }
    return messages.get(trend, "Tendance inconnue")


