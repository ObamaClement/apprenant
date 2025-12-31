"""Service d'inférence des connaissances à partir des interactions."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any
from uuid import UUID
from app.models.learner_competency_mastery import LearnerCompetencyMastery
from app.models.competence_clinique import CompetenceClinique
from app.models.interaction_log import InteractionLog
from app.services.knowledge_update_service import update_mastery, calculate_confidence


def infer_knowledge_from_interaction(
    db: Session,
    learner_id: int,
    competence_id: int,
    score: float,
    correct: bool = None
) -> LearnerCompetencyMastery:
    """
    Mettre à jour la maîtrise d'une compétence basée sur une interaction.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        competence_id: ID de la compétence
        score: Score obtenu (0-100)
        correct: Réponse correcte ? (optionnel)
    
    Returns:
        LearnerCompetencyMastery mis à jour
    """
    # Récupérer la compétence pour les paramètres BKT
    competence = db.query(CompetenceClinique).filter(CompetenceClinique.id == competence_id).first()
    
    # Récupérer ou créer l'enregistrement de maîtrise
    mastery = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id,
        LearnerCompetencyMastery.competence_id == competence_id
    ).first()
    
    if not mastery:
        mastery = LearnerCompetencyMastery(
            learner_id=learner_id,
            competence_id=competence_id,
            mastery_level=competence.p_init if competence else 0.2,
            nb_success=0,
            nb_failures=0,
            streak_correct=0
        )
        db.add(mastery)
        db.flush()
    
    # Mettre à jour les statistiques
    is_correct = correct if correct is not None else (score >= 50)
    
    if is_correct:
        mastery.nb_success = (mastery.nb_success or 0) + 1
        mastery.streak_correct = (mastery.streak_correct or 0) + 1
    else:
        mastery.nb_failures = (mastery.nb_failures or 0) + 1
        mastery.streak_correct = 0
    
    # Mettre à jour le niveau de maîtrise avec BKT
    if competence:
        new_mastery = update_mastery(
            mastery.mastery_level or 0.2,
            score,
            correct=correct,
            p_transit=competence.p_transit,
            p_guess=competence.p_guess,
            p_slip=competence.p_slip,
        )
    else:
        new_mastery = update_mastery(mastery.mastery_level or 0.2, score, correct=correct)
    
    mastery.mastery_level = new_mastery
    mastery.last_practice_date = func.now()
    
    # Calculer la confiance
    mastery.confidence = calculate_confidence(
        mastery.nb_success or 0,
        mastery.nb_failures or 0,
        mastery.streak_correct or 0
    )
    
    db.commit()
    db.refresh(mastery)
    return mastery


def infer_knowledge_from_session(
    db: Session,
    session_id: UUID,
    competence_scores: Dict[int, float]
) -> List[LearnerCompetencyMastery]:
    """
    Mettre à jour les maîtrises basées sur toutes les interactions d'une session.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        competence_scores: Dictionnaire {competence_id: score}
    
    Returns:
        Liste des maîtrises mises à jour
    """
    from app.models.simulation_session import SimulationSession
    
    # Récupérer la session
    session = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} non trouvée")
    
    updated_masteries = []
    
    for competence_id, score in competence_scores.items():
        mastery = infer_knowledge_from_interaction(
            db,
            session.learner_id,
            competence_id,
            score
        )
        updated_masteries.append(mastery)
    
    return updated_masteries


def extract_competences_from_actions(
    db: Session,
    session_id: UUID
) -> Dict[int, List[float]]:
    """
    Extraire les compétences sollicitées et leurs scores depuis les interactions.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
    
    Returns:
        Dictionnaire {competence_id: [liste de scores]}
    """
    interactions = db.query(InteractionLog).filter(
        InteractionLog.session_id == session_id
    ).all()
    
    competence_scores: Dict[int, List[float]] = {}
    
    for interaction in interactions:
        if not interaction.action_content:
            continue
        
        # Extraire competence_id et score du contenu JSON
        content = interaction.action_content
        if isinstance(content, dict):
            comp_id = content.get('competence_id')
            score = content.get('score')
            
            if comp_id and score is not None:
                if comp_id not in competence_scores:
                    competence_scores[comp_id] = []
                competence_scores[comp_id].append(float(score))
    
    return competence_scores


def get_learner_knowledge_summary(
    db: Session,
    learner_id: int
) -> Dict[str, Any]:
    """
    Obtenir un résumé des connaissances d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire avec statistiques
    """
    masteries = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id
    ).all()
    
    if not masteries:
        return {
            "learner_id": learner_id,
            "total_competences": 0,
            "average_mastery": 0.0,
            "mastered_competences": 0,
            "competences": []
        }
    
    total_mastery = sum(m.mastery_level or 0 for m in masteries)
    average_mastery = total_mastery / len(masteries)
    mastered = sum(1 for m in masteries if (m.mastery_level or 0) >= 0.8)
    
    # Détails par compétence
    competences_details = []
    for m in masteries:
        comp = db.query(CompetenceClinique).filter(CompetenceClinique.id == m.competence_id).first()
        competences_details.append({
            "competence_id": m.competence_id,
            "competence_code": comp.code_competence if comp else "Unknown",
            "competence_nom": comp.nom if comp else "Unknown",
            "mastery_level": round(m.mastery_level or 0, 2),
            "confidence": round(m.confidence or 0, 2),
            "nb_success": m.nb_success or 0,
            "nb_failures": m.nb_failures or 0,
            "last_practice": m.last_practice_date
        })
    
    # Trier par niveau de maîtrise décroissant
    competences_details.sort(key=lambda x: x["mastery_level"], reverse=True)
    
    return {
        "learner_id": learner_id,
        "total_competences": len(masteries),
        "average_mastery": round(average_mastery, 2),
        "mastered_competences": mastered,
        "competences": competences_details
    }


def identify_weak_competences(
    db: Session,
    learner_id: int,
    threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Identifier les compétences faibles d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        threshold: Seuil de maîtrise
    
    Returns:
        Liste des compétences faibles
    """
    masteries = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id,
        LearnerCompetencyMastery.mastery_level < threshold
    ).all()
    
    weak_competences = []
    for m in masteries:
        comp = db.query(CompetenceClinique).filter(CompetenceClinique.id == m.competence_id).first()
        weak_competences.append({
            "competence_id": m.competence_id,
            "competence_code": comp.code_competence if comp else "Unknown",
            "competence_nom": comp.nom if comp else "Unknown",
            "mastery_level": round(m.mastery_level or 0, 2),
            "nb_failures": m.nb_failures or 0,
            "priority": "haute" if (m.mastery_level or 0) < 0.3 else "moyenne"
        })
    
    # Trier par niveau de maîtrise croissant (les plus faibles en premier)
    weak_competences.sort(key=lambda x: x["mastery_level"])
    
    return weak_competences