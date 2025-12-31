"""Routes FastAPI pour l'état affectif - COMPATIBLE STI."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.deps import get_db
from app.models.learner_affective import LearnerAffectiveState
from app.models.simulation_session import SimulationSession
from app.models.learner import Learner
from app.schemas.learner_affective import (
    LearnerAffectiveCreate,
    LearnerAffectiveResponse,
    LearnerAffectiveUpdate
)
from app.services.affective_service import (
    update_affective_state,
    record_affective_state,
    get_latest_affective_state,
    get_affective_profile,
    get_feedback_type
)

router = APIRouter(prefix="/affective", tags=["Learner Affective"])


@router.post("/", response_model=LearnerAffectiveResponse, status_code=201)
def create_affective_state(
    data: LearnerAffectiveCreate,
    db: Session = Depends(get_db)
):
    """Enregistrer un nouvel état affectif pour une session."""
    # Vérifier que la session existe
    session = db.query(SimulationSession).filter(
        SimulationSession.id == data.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    affective = record_affective_state(
        db,
        data.session_id,
        data.stress_level,
        data.confidence_level,
        data.motivation_level,
        data.frustration_level
    )
    
    return affective


@router.get("/session/{session_id}", response_model=list[LearnerAffectiveResponse])
def get_session_affective_states(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupérer tous les états affectifs d'une session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    states = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.session_id == session_id
    ).order_by(LearnerAffectiveState.timestamp).all()
    
    return states


@router.get("/latest/{learner_id}", response_model=LearnerAffectiveResponse)
def get_latest_learner_affective(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer le dernier état affectif d'un apprenant (toutes sessions)."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Trouver la dernière session
    latest_session = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).order_by(SimulationSession.start_time.desc()).first()
    
    if not latest_session:
        raise HTTPException(status_code=404, detail="Aucune session trouvée")
    
    affective = get_latest_affective_state(db, latest_session.id)
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    return affective


@router.post("/update-from-score")
def update_from_score(
    session_id: UUID = Query(...),
    score: float = Query(..., ge=0.0, le=100.0),
    db: Session = Depends(get_db)
):
    """Mettre à jour l'état affectif basé sur un score."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Récupérer le dernier état
    latest = get_latest_affective_state(db, session_id)
    
    if latest:
        motivation, frustration, confidence, stress = update_affective_state(
            latest.motivation_level or 0.5,
            latest.frustration_level or 0.0,
            latest.confidence_level or 0.5,
            latest.stress_level or 0.0,
            score
        )
    else:
        motivation, frustration, confidence, stress = update_affective_state(
            0.5, 0.0, 0.5, 0.0, score
        )
    
    # Enregistrer le nouvel état
    new_affective = record_affective_state(
        db, session_id, stress, confidence, motivation, frustration
    )
    
    return {
        "session_id": str(session_id),
        "score": score,
        "motivation": motivation,
        "frustration": frustration,
        "confidence": confidence,
        "stress": stress,
        "message": "État affectif mis à jour"
    }


@router.get("/profile/session/{session_id}")
def get_profile_for_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtenir le profil affectif pour une session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    affective = get_latest_affective_state(db, session_id)
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    profile = get_affective_profile(
        affective.motivation_level or 0.5,
        affective.frustration_level or 0.0,
        affective.confidence_level or 0.5,
        affective.stress_level or 0.0
    )
    
    return profile


@router.get("/feedback-type/session/{session_id}")
def get_feedback_for_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtenir le type de feedback recommandé pour une session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    affective = get_latest_affective_state(db, session_id)
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    feedback_type = get_feedback_type(
        affective.motivation_level or 0.5,
        affective.frustration_level or 0.0,
        affective.confidence_level or 0.5,
        affective.stress_level or 0.0
    )
    
    return {
        "session_id": str(session_id),
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


@router.get("/history/{learner_id}")
def get_affective_history(
    learner_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer l'historique des états affectifs d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Récupérer les sessions de l'apprenant
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).order_by(SimulationSession.start_time.desc()).limit(limit).all()
    
    history = []
    for session in sessions:
        affective = get_latest_affective_state(db, session.id)
        if affective:
            history.append({
                "session_id": str(session.id),
                "timestamp": affective.timestamp,
                "motivation": affective.motivation_level,
                "frustration": affective.frustration_level,
                "confidence": affective.confidence_level,
                "stress": affective.stress_level,
                "score_session": session.score_final
            })
    
    return {
        "learner_id": learner_id,
        "history_count": len(history),
        "history": history
    }


@router.get("/evolution/{learner_id}")
def get_affective_evolution(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Analyser l'évolution de l'état affectif d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Récupérer toutes les sessions
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).order_by(SimulationSession.start_time).all()
    
    if not sessions:
        return {
            "learner_id": learner_id,
            "message": "Aucune donnée disponible"
        }
    
    # Collecter les données
    motivation_values = []
    frustration_values = []
    confidence_values = []
    stress_values = []
    
    for session in sessions:
        affective = get_latest_affective_state(db, session.id)
        if affective:
            if affective.motivation_level is not None:
                motivation_values.append(affective.motivation_level)
            if affective.frustration_level is not None:
                frustration_values.append(affective.frustration_level)
            if affective.confidence_level is not None:
                confidence_values.append(affective.confidence_level)
            if affective.stress_level is not None:
                stress_values.append(affective.stress_level)
    
    # Calculer les moyennes
    def safe_avg(values):
        return sum(values) / len(values) if values else 0.0
    
    # Déterminer les tendances
    def get_trend(values):
        if len(values) < 2:
            return "stable"
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        avg_first = safe_avg(first_half)
        avg_second = safe_avg(second_half)
        diff = avg_second - avg_first
        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        return "stable"
    
    return {
        "learner_id": learner_id,
        "sessions_analyzed": len(sessions),
        "averages": {
            "motivation": round(safe_avg(motivation_values), 2),
            "frustration": round(safe_avg(frustration_values), 2),
            "confidence": round(safe_avg(confidence_values), 2),
            "stress": round(safe_avg(stress_values), 2)
        },
        "trends": {
            "motivation": get_trend(motivation_values),
            "frustration": get_trend(frustration_values),
            "confidence": get_trend(confidence_values),
            "stress": get_trend(stress_values)
        },
        "current_state": {
            "motivation": motivation_values[-1] if motivation_values else None,
            "frustration": frustration_values[-1] if frustration_values else None,
            "confidence": confidence_values[-1] if confidence_values else None,
            "stress": stress_values[-1] if stress_values else None
        }
    }


@router.put("/{affective_id}", response_model=LearnerAffectiveResponse)
def update_affective_state_endpoint(
    affective_id: int,
    update_data: LearnerAffectiveUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un état affectif."""
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.id == affective_id
    ).first()
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(affective, field, value)
    
    db.commit()
    db.refresh(affective)
    return affective


@router.delete("/{affective_id}", status_code=204)
def delete_affective_state(
    affective_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un état affectif."""
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.id == affective_id
    ).first()
    if not affective:
        raise HTTPException(status_code=404, detail="État affectif non trouvé")
    
    db.delete(affective)
    db.commit()
    return None