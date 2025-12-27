"""Service d'inférence et de mise à jour automatique des connaissances."""
from sqlalchemy.orm import Session
from app.models.learner_knowledge import LearnerKnowledge
from app.models.learning_history import LearningHistory
from app.models.concept import Concept
from app.services.knowledge_update_service import update_mastery


def infer_knowledge_from_activity(
    db: Session,
    learner_id: int,
    concept_id: int,
    score: float
) -> LearnerKnowledge:
    """
    Mettre à jour le niveau de maîtrise d'un concept basé sur une activité.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        concept_id: ID du concept
        score: Score obtenu (0-100)
    
    Returns:
        LearnerKnowledge mis à jour
    """
    concept = db.query(Concept).get(concept_id)

    # Récupérer ou créer l'enregistrement de connaissances
    lk = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id,
        LearnerKnowledge.concept_id == concept_id
    ).first()
    if not lk:
        lk = LearnerKnowledge(
            learner_id=learner_id,
            concept_id=concept_id,
            mastery_level=concept.p_init if concept else 0.2
        )
        db.add(lk)
     
    # Mettre à jour le niveau de maîtrise
    if concept:
        lk.mastery_level = update_mastery(
            lk.mastery_level,
            score,
            p_transit=concept.p_transit,
            p_guess=concept.p_guess,
            p_slip=concept.p_slip,
        )
    else:
        lk.mastery_level = update_mastery(lk.mastery_level, score)
    
    db.commit()
    db.refresh(lk)
    
    return lk


def infer_knowledge_from_history(
    db: Session,
    learner_id: int,
    concept_id: int
) -> LearnerKnowledge:
    """
    Inférer le niveau de maîtrise à partir de l'historique d'apprentissage.
    
    Calcule une moyenne pondérée des scores pour ce concept.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        concept_id: ID du concept
    
    Returns:
        LearnerKnowledge mis à jour
    """
    concept = db.query(Concept).get(concept_id)

    # Récupérer tous les historiques avec scores pour ce concept
    histories = db.query(LearningHistory).filter(
        LearningHistory.learner_id == learner_id,
        LearningHistory.activity_ref.like(f"%{concept_id}%"),
        LearningHistory.score.isnot(None),
    ).order_by(LearningHistory.created_at.asc()).all()
    if not histories:
        return None

    mastery_level = concept.p_init if concept else 0.2
    for h in histories:
        if concept:
            mastery_level = update_mastery(
                mastery_level,
                h.score,
                correct=h.success,
                p_transit=concept.p_transit,
                p_guess=concept.p_guess,
                p_slip=concept.p_slip,
            )
        else:
            mastery_level = update_mastery(mastery_level, h.score, correct=h.success)
    
    # Récupérer ou créer l'enregistrement
    lk = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id,
        LearnerKnowledge.concept_id == concept_id
    ).first()
    if not lk:
        lk = LearnerKnowledge(
            learner_id=learner_id,
            concept_id=concept_id,
            mastery_level=mastery_level
        )
        db.add(lk)
    else:
        lk.mastery_level = mastery_level
    
    db.commit()
    db.refresh(lk)
    
    return lk


def get_learner_knowledge_summary(
    db: Session,
    learner_id: int
) -> dict:
    """
    Obtenir un résumé des connaissances d'un  apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire avec statistiques de connaissances
    """
    knowledge_records = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id
    ).all()
    
    if not knowledge_records:
        return {
            "learner_id": learner_id,
            "total_concepts": 0,
            "average_mastery": 0.0,
            "mastered_concepts": 0,
            "concepts": []
        }
    
    total_mastery = sum(k.mastery_level for k in knowledge_records)
    average_mastery = total_mastery / len(knowledge_records)
    mastered = sum(1 for k in knowledge_records if k.mastery_level >= 0.8)
    
    return {
        "learner_id": learner_id,
        "total_concepts": len(knowledge_records),
        "average_mastery": round(average_mastery, 2),
        "mastered_concepts": mastered,
        "concepts": [
            {
                "concept_id": k.concept_id,
                "concept_name": k.concept.name if k.concept else "Unknown",
                "mastery_level": round(k.mastery_level, 2)
            }
            for k in knowledge_records
        ]
    }
