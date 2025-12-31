"""Service pour les sessions de simulation."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.simulation_session import SimulationSession
from app.models.learner import Learner
from app.models.cas_clinique import CasCliniqueEnrichi


def create_session(
    db: Session,
    learner_id: int,
    cas_clinique_id: int
) -> SimulationSession:
    """
    Créer une nouvelle session de simulation.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        cas_clinique_id: ID du cas clinique
    
    Returns:
        Session créée
    """
    # Vérifier que l'apprenant existe
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise ValueError(f"Apprenant {learner_id} non trouvé")
    
    # Vérifier que le cas existe
    case = db.query(CasCliniqueEnrichi).filter(CasCliniqueEnrichi.id == cas_clinique_id).first()
    if not case:
        raise ValueError(f"Cas clinique {cas_clinique_id} non trouvé")
    
    # Créer la session
    session = SimulationSession(
        learner_id=learner_id,
        cas_clinique_id=cas_clinique_id,
        statut="en_cours",
        current_stage="anamnese"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Incrémenter le compteur d'utilisation du cas
    from app.services.cas_clinique_service import increment_case_usage
    increment_case_usage(db, cas_clinique_id)
    
    return session


def get_session_by_id(db: Session, session_id: UUID) -> Optional[SimulationSession]:
    """
    Récupérer une session par ID.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
    
    Returns:
        Session ou None
    """
    return db.query(SimulationSession).filter(SimulationSession.id == session_id).first()


def get_sessions_by_learner(
    db: Session,
    learner_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[SimulationSession]:
    """
    Récupérer les sessions d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
    
    Returns:
        Liste des sessions
    """
    return db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).order_by(SimulationSession.start_time.desc()).offset(skip).limit(limit).all()


def update_session_stage(
    db: Session,
    session_id: UUID,
    new_stage: str
) -> Optional[SimulationSession]:
    """
    Mettre à jour l'étape courante d'une session.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        new_stage: Nouvelle étape
    
    Returns:
        Session mise à jour ou None
    """
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    session.current_stage = new_stage
    db.commit()
    db.refresh(session)
    return session


def complete_session(
    db: Session,
    session_id: UUID,
    score_final: float,
    raison_fin: str = "completed",
    diagnostic_correct: bool = False
) -> Optional[SimulationSession]:
    """
    Terminer une session de simulation.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        score_final: Score final (0-100)
        raison_fin: Raison de fin
        diagnostic_correct: Le diagnostic était-il correct ?
    
    Returns:
        Session terminée ou None
    """
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    # Calculer le temps total
    if session.start_time:
        temps_total = int((datetime.now() - session.start_time.replace(tzinfo=None)).total_seconds())
    else:
        temps_total = 0
    
    # Mettre à jour la session
    session.end_time = func.now()
    session.temps_total = temps_total
    session.score_final = score_final
    session.statut = "termine"
    session.raison_fin = raison_fin
    
    db.commit()
    db.refresh(session)
    
    # Mettre à jour les statistiques du cas
    from app.services.cas_clinique_service import update_case_statistics
    update_case_statistics(db, session.cas_clinique_id, score_final, diagnostic_correct)
    
    return session


def abandon_session(
    db: Session,
    session_id: UUID,
    raison: str = "abandoned"
) -> Optional[SimulationSession]:
    """
    Abandonner une session en cours.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        raison: Raison de l'abandon
    
    Returns:
        Session abandonnée ou None
    """
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    session.end_time = func.now()
    session.statut = "abandonne"
    session.raison_fin = raison
    
    db.commit()
    db.refresh(session)
    return session


def get_active_session(
    db: Session,
    learner_id: int
) -> Optional[SimulationSession]:
    """
    Récupérer la session active d'un apprenant (s'il y en a une).
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Session active ou None
    """
    return db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id,
        SimulationSession.statut == "en_cours"
    ).first()


def get_session_statistics(
    db: Session,
    learner_id: int
) -> dict:
    """
    Obtenir les statistiques des sessions d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire avec statistiques
    """
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).all()
    
    if not sessions:
        return {
            "total_sessions": 0,
            "completed_sessions": 0,
            "average_score": 0.0,
            "total_time_spent": 0
        }
    
    completed = [s for s in sessions if s.statut == "termine"]
    scores = [s.score_final for s in completed if s.score_final is not None]
    
    return {
        "total_sessions": len(sessions),
        "completed_sessions": len(completed),
        "abandoned_sessions": len([s for s in sessions if s.statut == "abandonne"]),
        "average_score": sum(scores) / len(scores) if scores else 0.0,
        "best_score": max(scores) if scores else 0.0,
        "total_time_spent": sum(s.temps_total or 0 for s in completed)
    }