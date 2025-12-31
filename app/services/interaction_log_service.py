"""Service pour les logs d'interaction."""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.models.interaction_log import InteractionLog
from app.models.simulation_session import SimulationSession


def create_interaction(
    db: Session,
    session_id: UUID,
    action_type: str,
    action_category: Optional[str] = None,
    action_content: Optional[Dict[str, Any]] = None,
    response_latency: Optional[int] = None
) -> InteractionLog:
    """
    Enregistrer une interaction.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        action_type: Type d'action
        action_category: Catégorie d'action
        action_content: Contenu de l'action (JSON)
        response_latency: Latence de réponse (ms)
    
    Returns:
        Log d'interaction créé
    """
    # Vérifier que la session existe
    session = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} non trouvée")
    
    # Créer le log
    log = InteractionLog(
        session_id=session_id,
        action_type=action_type,
        action_category=action_category,
        action_content=action_content,
        response_latency=response_latency
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def create_interactions_batch(
    db: Session,
    session_id: UUID,
    actions: List[Dict[str, Any]]
) -> List[InteractionLog]:
    """
    Enregistrer plusieurs interactions en batch.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        actions: Liste des actions à enregistrer
    
    Returns:
        Liste des logs créés
    """
    logs = []
    
    for action in actions:
        log = InteractionLog(
            session_id=session_id,
            action_type=action.get('action_type'),
            action_category=action.get('action_category'),
            action_content=action.get('action_content'),
            response_latency=action.get('response_latency')
        )
        db.add(log)
        logs.append(log)
    
    db.commit()
    
    for log in logs:
        db.refresh(log)
    
    return logs


def get_interactions_by_session(
    db: Session,
    session_id: UUID
) -> List[InteractionLog]:
    """
    Récupérer toutes les interactions d'une session.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
    
    Returns:
        Liste des interactions
    """
    return db.query(InteractionLog).filter(
        InteractionLog.session_id == session_id
    ).order_by(InteractionLog.timestamp).all()


def get_interactions_by_category(
    db: Session,
    session_id: UUID,
    category: str
) -> List[InteractionLog]:
    """
    Récupérer les interactions d'une catégorie donnée.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        category: Catégorie d'action
    
    Returns:
        Liste des interactions
    """
    return db.query(InteractionLog).filter(
        InteractionLog.session_id == session_id,
        InteractionLog.action_category == category
    ).order_by(InteractionLog.timestamp).all()


def get_interactions_by_type(
    db: Session,
    session_id: UUID,
    action_type: str
) -> List[InteractionLog]:
    """
    Récupérer les interactions d'un type donné.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        action_type: Type d'action
    
    Returns:
        Liste des interactions
    """
    return db.query(InteractionLog).filter(
        InteractionLog.session_id == session_id,
        InteractionLog.action_type == action_type
    ).order_by(InteractionLog.timestamp).all()


def mark_interaction_relevance(
    db: Session,
    interaction_id: int,
    est_pertinent: bool,
    charge_cognitive: Optional[float] = None
) -> Optional[InteractionLog]:
    """
    Marquer la pertinence d'une interaction.
    
    Args:
        db: Session de base de données
        interaction_id: ID de l'interaction
        est_pertinent: L'action était-elle pertinente ?
        charge_cognitive: Charge cognitive estimée
    
    Returns:
        Log mis à jour ou None
    """
    log = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    if not log:
        return None
    
    log.est_pertinent = est_pertinent
    if charge_cognitive is not None:
        log.charge_cognitive_estimee = charge_cognitive
    
    db.commit()
    db.refresh(log)
    return log


def analyze_session_interactions(
    db: Session,
    session_id: UUID
) -> Dict[str, Any]:
    """
    Analyser les interactions d'une session.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
    
    Returns:
        Statistiques d'analyse
    """
    interactions = get_interactions_by_session(db, session_id)
    
    if not interactions:
        return {
            "total_interactions": 0,
            "average_latency": 0,
            "pertinent_rate": 0.0,
            "categories": {}
        }
    
    # Statistiques globales
    latencies = [i.response_latency for i in interactions if i.response_latency]
    pertinent_count = sum(1 for i in interactions if i.est_pertinent is True)
    evaluated_count = sum(1 for i in interactions if i.est_pertinent is not None)
    
    # Par catégorie
    categories = {}
    for interaction in interactions:
        cat = interaction.action_category or "non_categorise"
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    return {
        "total_interactions": len(interactions),
        "average_latency": sum(latencies) / len(latencies) if latencies else 0,
        "pertinent_rate": (pertinent_count / evaluated_count * 100) if evaluated_count > 0 else 0.0,
        "categories": categories,
        "evaluated_interactions": evaluated_count
    }