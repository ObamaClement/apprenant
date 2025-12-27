"""Moteur d'adaptation intelligente - Orchestration des modèles."""
from sqlalchemy.orm import Session
from app.models.learner_knowledge import LearnerKnowledge
from app.models.learner_performance import LearnerPerformance
from app.models.learner_affective import LearnerAffectiveState
from app.models.learner_behavior import LearnerBehavior
from app.models.concept import Concept
from app.services.knowledge_update_service import update_mastery
from app.services.affective_service import (
    update_affective_state,
    get_affective_label,
    detect_frustration,
    detect_demotivation
)
from app.services.performance_service import performance_indicator


def process_new_performance(
    db: Session,
    learner_id: int,
    concept_id: int,
    score: float,
    activity_type: str = "exercice",
    time_spent: int = None
) -> dict:
    """
    Orchestration globale après une nouvelle performance.
    
    Flux:
    1. Enregistrer la performance
    2. Mettre à jour le niveau de maîtrise
    3. Mettre à jour l'état affectif
    4. Analyser le comportement
    5. Générer une recommandation pédagogique
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        concept_id: ID du concept
        score: Score obtenu (0-100)
        activity_type: Type d'activité (quiz, exercice, test)
        time_spent: Temps passé en secondes
    
    Returns:
        Dictionnaire avec résultats de l'adaptation
    """
    
    # 1️⃣ Enregistrer la performance
    performance = LearnerPerformance(
        learner_id=learner_id,
        concept_id=concept_id,
        activity_type=activity_type,
        score=score,
        time_spent=time_spent,
        attempts=1
    )
    db.add(performance)
    db.flush()
    
    # 2️⃣ Récupérer ou créer la connaissance
    knowledge = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id,
        LearnerKnowledge.concept_id == concept_id
    ).first()

    concept = db.query(Concept).get(concept_id)
    
    previous_mastery = 0.0
    if not knowledge:
        knowledge = LearnerKnowledge(
            learner_id=learner_id,
            concept_id=concept_id,
            mastery_level=concept.p_init if concept else 0.2
        )
        db.add(knowledge)
        db.flush()
    else:
        previous_mastery = knowledge.mastery_level
    
    # 3️⃣ Mettre à jour le niveau de maîtrise
    if concept:
        new_mastery = update_mastery(
            knowledge.mastery_level,
            score,
            p_transit=concept.p_transit,
            p_guess=concept.p_guess,
            p_slip=concept.p_slip,
        )
    else:
        new_mastery = update_mastery(knowledge.mastery_level, score)
    knowledge.mastery_level = new_mastery
    
    # 4️⃣ Récupérer ou créer l'état affectif
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    affective_changes = {}
    if affective:
        old_affective = {
            "motivation": affective.motivation,
            "frustration": affective.frustration,
            "confidence": affective.confidence,
            "stress": affective.stress
        }
        
        # Mettre à jour l'état affectif
        motivation, frustration, confidence, stress = update_affective_state(
            affective.motivation,
            affective.frustration,
            affective.confidence,
            affective.stress,
            score,
            previous_score=None
        )
        
        affective.motivation = motivation
        affective.frustration = frustration
        affective.confidence = confidence
        affective.stress = stress
        
        affective_changes = {
            "motivation": {"old": old_affective["motivation"], "new": motivation},
            "frustration": {"old": old_affective["frustration"], "new": frustration},
            "confidence": {"old": old_affective["confidence"], "new": confidence},
            "stress": {"old": old_affective["stress"], "new": stress}
        }
    else:
        # Créer un nouvel état affectif initial
        affective = LearnerAffectiveState(learner_id=learner_id)
        
        # Mettre à jour basé sur le score
        motivation, frustration, confidence, stress = update_affective_state(
            0.5, 0.0, 0.5, 0.0, score
        )
        
        affective.motivation = motivation
        affective.frustration = frustration
        affective.confidence = confidence
        affective.stress = stress
        
        db.add(affective)
        db.flush()
    
    # 5️⃣ Générer la recommandation pédagogique
    recommendation = _pedagogical_decision(
        new_mastery,
        affective,
        score
    )
    
    # 6️⃣ Récupérer le concept
    concept_name = concept.name if concept else "Unknown"
    
    # Commit toutes les modifications
    db.commit()
    
    return {
        "learner_id": learner_id,
        "concept_id": concept_id,
        "concept_name": concept_name,
        "score": score,
        "performance_indicator": performance_indicator(score),
        "knowledge": {
            "previous_mastery": round(previous_mastery, 2),
            "new_mastery": round(new_mastery, 2),
            "progress": round(new_mastery - previous_mastery, 2)
        },
        "affective": {
            "motivation": affective.motivation,
            "frustration": affective.frustration,
            "confidence": affective.confidence,
            "stress": affective.stress,
            "label": get_affective_label(
                affective.motivation,
                affective.frustration,
                affective.confidence,
                affective.stress
            ),
            "changes": affective_changes
        },
        "recommendation": recommendation,
        "next_action": _get_next_action(new_mastery, affective, score)
    }


def _pedagogical_decision(
    mastery_level: float,
    affective: LearnerAffectiveState,
    score: float
) -> str:
    """
    Prendre une décision pédagogique basée sur les modèles.
    
    Args:
        mastery_level: Niveau de maîtrise (0-1)
        affective: État affectif
        score: Score obtenu (0-100)
    
    Returns:
        Recommandation pédagogique
    """
    
    # Cas 1: Très faible maîtrise (< 0.3)
    if mastery_level < 0.3:
        if affective.frustration > 0.7:
            return "Revoir le concept avec des exemples très guidés et encourager l'apprenant"
        return "Revoir le cours avec des exemples guidés et des exercices simples"
    
    # Cas 2: Maîtrise faible (0.3-0.5)
    if mastery_level < 0.5:
        if affective.frustration > 0.6:
            return "Proposer une activité plus simple avec beaucoup de soutien"
        if score < 40:
            return "Proposer des exercices supplémentaires avec guidance progressive"
        return "Proposer des exercices de consolidation"
    
    # Cas 3: Maîtrise moyenne (0.5-0.7)
    if mastery_level < 0.7:
        if affective.stress > 0.6:
            return "Proposer un exercice standard avec moins de pression"
        if score >= 70:
            return "Proposer des exercices plus complexes pour progresser"
        return "Continuer avec des exercices standard"
    
    # Cas 4: Bonne maîtrise (0.7-0.85)
    if mastery_level < 0.85:
        if affective.confidence > 0.8:
            return "Proposer des exercices avancés pour consolider la maîtrise"
        return "Proposer des exercices intermédiaires"
    
    # Cas 5: Excellente maîtrise (>= 0.85)
    if affective.motivation > 0.8:
        return "Proposer des défis avancés et des extensions du concept"
    return "Proposer des applications pratiques du concept"


def _get_next_action(
    mastery_level: float,
    affective: LearnerAffectiveState,
    score: float
) -> dict:
    """
    Déterminer l'action suivante recommandée.
    
    Args:
        mastery_level: Niveau de maîtrise
        affective: État affectif
        score: Score obtenu
    
    Returns:
        Dictionnaire avec action recommandée
    """
    
    action = {
        "type": None,
        "priority": "normal",
        "description": None
    }
    
    # Intervention urgente si très frustré
    if detect_frustration(affective.frustration, threshold=0.8):
        action["type"] = "intervention"
        action["priority"] = "urgent"
        action["description"] = "Contacter l'apprenant pour offrir du soutien immédiat"
        return action
    
    # Intervention si frustré
    if detect_frustration(affective.frustration, threshold=0.6):
        action["type"] = "support"
        action["priority"] = "high"
        action["description"] = "Proposer une session de tutorat ou une aide supplémentaire"
        return action
    
    # Intervention si démotivé
    if detect_demotivation(affective.motivation, threshold=0.3):
        action["type"] = "motivation"
        action["priority"] = "high"
        action["description"] = "Proposer des activités plus engageantes et motivantes"
        return action
    
    # Progression si bon apprentissage
    if mastery_level >= 0.8 and score >= 80:
        action["type"] = "progression"
        action["priority"] = "normal"
        action["description"] = "Passer au concept suivant ou proposer des extensions"
        return action
    
    # Consolidation si apprentissage en cours
    if mastery_level >= 0.5 and score >= 60:
        action["type"] = "consolidation"
        action["priority"] = "normal"
        action["description"] = "Proposer des exercices de consolidation"
        return action
    
    # Remédiation si difficultés
    if mastery_level < 0.5 or score < 50:
        action["type"] = "remediation"
        action["priority"] = "high"
        action["description"] = "Proposer des activités de remédiation avec guidance"
        return action
    
    # Par défaut
    action["type"] = "standard"
    action["priority"] = "normal"
    action["description"] = "Continuer avec les activités standard"
    return action


def get_adaptation_summary(
    db: Session,
    learner_id: int
) -> dict:
    """
    Obtenir un résumé complet de l'adaptation pour un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Résumé de l'adaptation
    """
    
    # Récupérer les modèles
    knowledge_records = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id
    ).all()
    
    affective = db.query(LearnerAffectiveState).filter(
        LearnerAffectiveState.learner_id == learner_id
    ).first()
    
    behavior = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == learner_id
    ).first()
    
    performances = db.query(LearnerPerformance).filter(
        LearnerPerformance.learner_id == learner_id
    ).all()
    
    # Calculer les statistiques
    avg_mastery = sum(k.mastery_level for k in knowledge_records) / len(knowledge_records) if knowledge_records else 0.0
    avg_score = sum(p.score for p in performances) / len(performances) if performances else 0.0
    
    return {
        "learner_id": learner_id,
        "knowledge": {
            "total_concepts": len(knowledge_records),
            "average_mastery": round(avg_mastery, 2),
            "mastered_concepts": len([k for k in knowledge_records if k.mastery_level >= 0.8])
        },
        "performance": {
            "total_activities": len(performances),
            "average_score": round(avg_score, 2)
        },
        "affective": {
            "motivation": affective.motivation if affective else 0.5,
            "frustration": affective.frustration if affective else 0.0,
            "confidence": affective.confidence if affective else 0.5,
            "stress": affective.stress if affective else 0.0
        } if affective else None,
        "behavior": {
            "engagement_score": behavior.engagement_score if behavior else 0.0
        } if behavior else None,
        "overall_status": _compute_overall_status(
            avg_mastery,
            avg_score,
            affective
        )
    }


def _compute_overall_status(
    avg_mastery: float,
    avg_score: float,
    affective: LearnerAffectiveState = None
) -> str:
    """
    Calculer le statut global de l'apprenant.
    
    Args:
        avg_mastery: Maîtrise moyenne
        avg_score: Score moyen
        affective: État affectif
    
    Returns:
        Statut global
    """
    
    if avg_mastery >= 0.8 and avg_score >= 80:
        if affective and affective.motivation > 0.7:
            return "Excellent - Apprenant très performant et motivé"
        return "Excellent - Apprenant très performant"
    
    if avg_mastery >= 0.6 and avg_score >= 70:
        if affective and affective.frustration > 0.6:
            return "Bon - Apprenant performant mais frustré"
        return "Bon - Apprenant performant"
    
    if avg_mastery >= 0.4 and avg_score >= 50:
        if affective and affective.motivation < 0.3:
            return "Moyen - Apprenant en apprentissage mais démotivé"
        return "Moyen - Apprenant en apprentissage"
    
    if affective and affective.frustration > 0.7:
        return "Faible - Apprenant en difficulté et très frustré"
    
    return "Faible - Apprenant en difficulté"
