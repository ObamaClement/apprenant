"""Routes FastAPI pour les logs d'interaction - CRITIQUE."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.core.deps import get_db
from app.models.interaction_log import InteractionLog
from app.models.simulation_session import SimulationSession
from app.schemas.interaction_log import (
    InteractionLogCreate,
    InteractionLogResponse,
    InteractionLogUpdate,
    InteractionLogBatchCreate,
    InteractionLogWithContext
)
from app.services.interaction_log_service import (
    create_interaction,
    create_interactions_batch,
    get_interactions_by_session,
    get_interactions_by_category,
    get_interactions_by_type,
    mark_interaction_relevance,
    analyze_session_interactions
)

router = APIRouter(prefix="/interactions", tags=["Interaction Logs"])


@router.post("/", response_model=InteractionLogResponse, status_code=201)
def create_interaction_log(
    data: InteractionLogCreate,
    db: Session = Depends(get_db)
):
    """Enregistrer une interaction."""
    try:
        log = create_interaction(
            db,
            data.session_id,
            data.action_type,
            data.action_category,
            data.action_content,
            data.response_latency
        )
        return log
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement: {str(e)}")


@router.post("/batch", response_model=list[InteractionLogResponse], status_code=201)
def create_interactions_batch_endpoint(
    data: InteractionLogBatchCreate,
    db: Session = Depends(get_db)
):
    """Enregistrer plusieurs interactions en batch."""
    # Vérifier que la session existe
    session = db.query(SimulationSession).filter(
        SimulationSession.id == data.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    try:
        logs = create_interactions_batch(db, data.session_id, data.actions)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement batch: {str(e)}")


@router.get("/session/{session_id}", response_model=list[InteractionLogResponse])
def get_session_interactions(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les interactions d'une session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return get_interactions_by_session(db, session_id)


@router.get("/session/{session_id}/with-context", response_model=list[InteractionLogWithContext])
def get_session_interactions_with_context(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupérer les interactions avec contexte de session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    interactions = get_interactions_by_session(db, session_id)
    
    # Enrichir avec contexte
    enriched = []
    for interaction in interactions:
        interaction_dict = {
            **interaction.__dict__,
            "learner_id": session.learner_id,
            "cas_clinique_id": session.cas_clinique_id,
            "session_statut": session.statut
        }
        enriched.append(interaction_dict)
    
    return enriched


@router.get("/category/{session_id}/{category}", response_model=list[InteractionLogResponse])
def get_interactions_by_category_endpoint(
    session_id: UUID,
    category: str,
    db: Session = Depends(get_db)
):
    """Récupérer les interactions d'une catégorie donnée."""
    return get_interactions_by_category(db, session_id, category)


@router.get("/type/{session_id}/{action_type}", response_model=list[InteractionLogResponse])
def get_interactions_by_type_endpoint(
    session_id: UUID,
    action_type: str,
    db: Session = Depends(get_db)
):
    """Récupérer les interactions d'un type donné."""
    return get_interactions_by_type(db, session_id, action_type)


@router.put("/{interaction_id}/relevance", response_model=InteractionLogResponse)
def mark_relevance(
    interaction_id: int,
    est_pertinent: bool = Query(..., description="Action pertinente?"),
    charge_cognitive: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Marquer la pertinence d'une interaction."""
    log = mark_interaction_relevance(db, interaction_id, est_pertinent, charge_cognitive)
    
    if not log:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")
    
    return log


@router.get("/analyze/{session_id}")
def analyze_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Analyser les interactions d'une session."""
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return analyze_session_interactions(db, session_id)


@router.put("/{interaction_id}", response_model=InteractionLogResponse)
def update_interaction(
    interaction_id: int,
    update_data: InteractionLogUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une interaction."""
    log = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(log, field, value)
    
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une interaction."""
    log = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")
    
    db.delete(log)
    db.commit()
    return None
