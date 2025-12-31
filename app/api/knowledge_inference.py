from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID
from app.core.deps import get_db
from app.models.learner import Learner
from app.models.competence_clinique import CompetenceClinique
from app.models.simulation_session import SimulationSession
from app.services.knowledge_inference_service import (
    infer_knowledge_from_interaction,
    infer_knowledge_from_session,
    get_learner_knowledge_summary,
    identify_weak_competences
)
from app.services.knowledge_update_service import (
    update_mastery,
    calculate_mastery_from_history,
    get_mastery_label
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge Inference"])


@router.post("/infer-from-interaction")
def infer_from_interaction(
    learner_id: int = Body(...),
    competence_id: int = Body(...),
    score: float = Body(..., ge=0.0, le=100.0),
    correct: Optional[bool] = Body(None),
    db: Session = Depends(get_db)
):
    """Inférer la maîtrise depuis une interaction unique (BKT)."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    mastery = infer_knowledge_from_interaction(
        db, learner_id, competence_id, score, correct
    )
    
    return {
        "learner_id": learner_id,
        "competence_id": competence_id,
        "competence_code": competence.code_competence,
        "score": score,
        "mastery_level": round(mastery.mastery_level or 0, 2),
        "confidence": round(mastery.confidence or 0, 2),
        "mastery_label": get_mastery_label(mastery.mastery_level or 0),
        "nb_success": mastery.nb_success,
        "nb_failures": mastery.nb_failures,
        "message": "Maîtrise inférée avec succès"
    }


@router.post("/infer-from-session")
def infer_from_session(
    session_id: UUID = Body(...),
    competence_scores: Dict[int, float] = Body(...),
    db: Session = Depends(get_db)
):
    """Inférer les maîtrises depuis une session complète (BKT)."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    masteries = infer_knowledge_from_session(db, session_id, competence_scores)
    
    results = []
    for m in masteries:
        comp = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == m.competence_id
        ).first()
        
        results.append({
            "competence_id": m.competence_id,
            "competence_code": comp.code_competence if comp else None,
            "mastery_level": round(m.mastery_level or 0, 2),
            "confidence": round(m.confidence or 0, 2),
            "mastery_label": get_mastery_label(m.mastery_level or 0)
        })
    
    return {
        "session_id": str(session_id),
        "learner_id": session.learner_id,
        "competences_updated": len(results),
        "masteries": results
    }


@router.get("/summary/{learner_id}")
def get_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un résumé complet des connaissances."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_learner_knowledge_summary(db, learner_id)


@router.get("/weak/{learner_id}")
def get_weak(
    learner_id: int,
    threshold: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Identifier les compétences faibles."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    weak = identify_weak_competences(db, learner_id, threshold)
    
    return {
        "learner_id": learner_id,
        "threshold": threshold,
        "weak_competences_count": len(weak),
        "weak_competences": weak
    }


@router.post("/batch-update")
def batch_update(
    updates: list[Dict] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour plusieurs maîtrises en batch.
    
    Format: [
        {"learner_id": int, "competence_id": int, "score": float},
        ...
    ]
    """
    results = []
    
    for update in updates:
        try:
            learner_id = update.get("learner_id")
            competence_id = update.get("competence_id")
            score = update.get("score")
            
            if not all([learner_id, competence_id, score is not None]):
                results.append({
                    "status": "error",
                    "message": "Données manquantes"
                })
                continue
            
            mastery = infer_knowledge_from_interaction(
                db, learner_id, competence_id, score
            )
            
            results.append({
                "status": "success",
                "learner_id": learner_id,
                "competence_id": competence_id,
                "mastery_level": round(mastery.mastery_level or 0, 2)
            })
        
        except Exception as e:
            results.append({
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total": len(updates),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"]),
        "results": results
    }


@router.post("/calculate-from-history")
def calculate_from_history(
    scores: list[float] = Body(...),
    db: Session = Depends(get_db)
):
    """Calculer le niveau de maîtrise à partir d'un historique de scores."""
    if not scores:
        raise HTTPException(status_code=400, detail="Liste de scores vide")
    
    # Valider les scores
    for score in scores:
        if not 0 <= score <= 100:
            raise HTTPException(
                status_code=400,
                detail=f"Score invalide: {score}. Doit être entre 0 et 100."
            )
    
    mastery_level = calculate_mastery_from_history(scores)
    
    return {
        "scores_count": len(scores),
        "scores": scores,
        "mastery_level": round(mastery_level, 2),
        "mastery_label": get_mastery_label(mastery_level),
        "message": "Maîtrise calculée depuis l'historique"
    }

