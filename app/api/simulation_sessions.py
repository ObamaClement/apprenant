### FICHIER 1: app/api/routes/simulation_sessions.py
"""Routes FastAPI pour les sessions de simulation - CRITIQUE."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.core.deps import get_db
from app.models.simulation_session import SimulationSession
from app.models.learner import Learner
from app.models.cas_clinique import CasCliniqueEnrichi
from app.schemas.simulation_session import (
    SimulationSessionCreate,
    SimulationSessionResponse,
    SimulationSessionUpdate,
    SimulationSessionComplete,
    SimulationSessionWithDetails
)
from app.services.simulation_session_service import (
    create_session,
    get_session_by_id,
    get_sessions_by_learner,
    update_session_stage,
    complete_session,
    abandon_session,
    get_active_session,
    get_session_statistics
)

router = APIRouter(prefix="/sessions", tags=["Simulation Sessions"])


@router.post("/start", response_model=SimulationSessionResponse, status_code=201)
def start_simulation_session(
    data: SimulationSessionCreate,
    db: Session = Depends(get_db)
):
    """Démarrer une nouvelle session de simulation."""
    try:
        session = create_session(db, data.learner_id, data.cas_clinique_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/{session_id}", response_model=SimulationSessionResponse)
def get_simulation_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupérer les détails d'une session."""
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    return session


@router.get("/{session_id}/details", response_model=SimulationSessionWithDetails)
def get_simulation_session_details(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Récupérer les détails enrichis d'une session."""
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Enrichir avec détails
    learner = db.query(Learner).filter(Learner.id == session.learner_id).first()
    case = db.query(CasCliniqueEnrichi).filter(CasCliniqueEnrichi.id == session.cas_clinique_id).first()
    
    from app.models.interaction_log import InteractionLog
    nb_interactions = db.query(InteractionLog).filter(
        InteractionLog.session_id == session_id
    ).count()
    
    session_dict = {
        **session.__dict__,
        "learner_nom": learner.nom if learner else None,
        "learner_matricule": learner.matricule if learner else None,
        "cas_code_fultang": case.code_fultang if case else None,
        "cas_niveau_difficulte": case.niveau_difficulte if case else None,
        "nb_interactions": nb_interactions
    }
    
    return session_dict


@router.get("/learner/{learner_id}", response_model=list[SimulationSessionResponse])
def get_learner_sessions(
    learner_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer toutes les sessions d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_sessions_by_learner(db, learner_id, skip, limit)


@router.get("/active/{learner_id}", response_model=SimulationSessionResponse)
def get_learner_active_session(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer la session active d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    session = get_active_session(db, learner_id)
    if not session:
        raise HTTPException(status_code=404, detail="Aucune session active")
    
    return session


@router.put("/{session_id}/stage", response_model=SimulationSessionResponse)
def update_stage(
    session_id: UUID,
    new_stage: str = Query(..., description="Nouvelle étape"),
    db: Session = Depends(get_db)
):
    """Mettre à jour l'étape courante d'une session."""
    valid_stages = ["anamnese", "examen_physique", "examens_complementaires", 
                    "diagnostic", "traitement", "termine"]
    
    if new_stage not in valid_stages:
        raise HTTPException(
            status_code=400, 
            detail=f"Étape invalide. Valeurs possibles: {', '.join(valid_stages)}"
        )
    
    session = update_session_stage(db, session_id, new_stage)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return session


@router.post("/{session_id}/complete", response_model=SimulationSessionResponse)
def complete_simulation(
    session_id: UUID,
    completion_data: SimulationSessionComplete,
    diagnostic_correct: bool = Query(..., description="Diagnostic correct?"),
    db: Session = Depends(get_db)
):
    """Terminer une session de simulation."""
    session = complete_session(
        db,
        session_id,
        completion_data.score_final,
        completion_data.raison_fin,
        diagnostic_correct
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return session


@router.post("/{session_id}/abandon", response_model=SimulationSessionResponse)
def abandon_simulation(
    session_id: UUID,
    raison: str = Query("abandoned", description="Raison de l'abandon"),
    db: Session = Depends(get_db)
):
    """Abandonner une session en cours."""
    session = abandon_session(db, session_id, raison)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return session


@router.get("/stats/{learner_id}")
def get_learner_session_stats(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques des sessions d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_session_statistics(db, learner_id)


@router.put("/{session_id}", response_model=SimulationSessionResponse)
def update_session(
    session_id: UUID,
    update_data: SimulationSessionUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une session."""
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Mettre à jour uniquement les champs fournis
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
### FICHIER 2: app/api/routes/interaction_logs.py


# ============================================================================
### FICHIER 3: app/api/routes/cas_cliniques.py
"""Routes FastAPI pour les cas cliniques - CRITIQUE."""
