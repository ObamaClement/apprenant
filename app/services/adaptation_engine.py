"""Moteur d'adaptation intelligente - Orchestration complète."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any
from uuid import UUID
from app.models.simulation_session import SimulationSession
from app.models.learner_competency_mastery import LearnerCompetencyMastery
from app.models.learner_affective import LearnerAffectiveState
from app.models.learner_behavior import LearnerBehavior
from app.models.cas_clinique import CasCliniqueEnrichi
from app.services.knowledge_inference_service import (
    infer_knowledge_from_interaction,
    extract_competences_from_actions
)
from app.services.affective_service import (
    update_affective_state,
    record_affective_state,
    get_latest_affective_state,
    get_affective_label
)
from app.services.simulation_session_service import complete_session
from app.services.interaction_log_service import create_interactions_batch


def process_simulation_completion(
    db: Session,
    session_id: UUID,
    actions: List[Dict[str, Any]],
    diagnostic_propose: str,
    diagnostic_correct: bool
) -> Dict[str, Any]:
    """
    Orchestration complète après une simulation de cas clinique.
    
    Flux:
    1. Enregistrer toutes les actions (InteractionLog)
    2. Extraire et mettre à jour les maîtrises de compétences (BKT)
    3. Calculer le score final de la session
    4. Mettre à jour l'état affectif
    5. Mettre à jour le comportement
    6. Générer une recommandation pédagogique
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        actions: Liste des actions effectuées
        diagnostic_propose: Diagnostic proposé par l'apprenant
        diagnostic_correct: Le diagnostic était-il correct ?
    
    Returns:
        Résultats complets de l'adaptation
    """
    # Récupérer la session
    session = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} non trouvée")
    
    learner_id = session.learner_id
    
    # 1️⃣ Enregistrer les actions (batch)
    if actions:
        create_interactions_batch(db, session_id, actions)
    
    # 2️⃣ Extraire les compétences sollicitées et leurs scores
    competence_scores = extract_competences_from_actions(db, session_id)
    
    # Mettre à jour les maîtrises (BKT)
    updated_masteries = []
    for comp_id, scores in competence_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        mastery = infer_knowledge_from_interaction(db, learner_id, comp_id, avg_score)
        updated_masteries.append({
            "competence_id": comp_id,
            "mastery_level": round(mastery.mastery_level or 0, 2),
            "confidence": round(mastery.confidence or 0, 2)
        })
    
    # 3️⃣ Calculer le score final de la session
    score_final = _calculate_session_score(
        competence_scores,
        diagnostic_correct,
        actions
    )
    
    # 4️⃣ Terminer la session
    session = complete_session(db, session_id, score_final, "completed", diagnostic_correct)
    
    # 5️⃣ Mettre à jour l'état affectif
    affective_result = _update_session_affective_state(db, session_id, learner_id, score_final)
    
    # 6️⃣ Mettre à jour le comportement
    _update_learner_behavior(db, learner_id, session.temps_total or 0)
    
    # 7️⃣ Générer la recommandation pédagogique
    recommendation = _generate_pedagogical_recommendation(
        db,
        learner_id,
        score_final,
        updated_masteries,
        affective_result
    )
    
    # 8️⃣ Déterminer l'action suivante
    next_action = _get_next_action(
        score_final,
        updated_masteries,
        affective_result
    )
    
    return {
        "session_id": str(session_id),
        "learner_id": learner_id,
        "cas_clinique_id": session.cas_clinique_id,
        "score_final": score_final,
        "diagnostic_correct": diagnostic_correct,
        "temps_total": session.temps_total,
        "competences_updated": updated_masteries,
        "affective_state": affective_result,
        "recommendation": recommendation,
        "next_action": next_action
    }


def _calculate_session_score(
    competence_scores: Dict[int, List[float]],
    diagnostic_correct: bool,
    actions: List[Dict[str, Any]]
) -> float:
    """
    Calculer le score final d'une session.
    
    Args:
        competence_scores: Scores par compétence
        diagnostic_correct: Diagnostic correct ?
        actions: Liste des actions
    
    Returns:
        Score final (0-100)
    """
    if not competence_scores:
        # Si pas de compétences évaluées, se baser sur le diagnostic
        return 80.0 if diagnostic_correct else 20.0
    
    # Calculer la moyenne des scores des compétences
    all_scores = []
    for scores in competence_scores.values():
        all_scores.extend(scores)
    
    avg_competence_score = sum(all_scores) / len(all_scores) if all_scores else 50.0
    
    # Pondération : 60% compétences, 40% diagnostic
    diagnostic_score = 100.0 if diagnostic_correct else 0.0
    final_score = (avg_competence_score * 0.6) + (diagnostic_score * 0.4)
    
    return round(min(100.0, max(0.0, final_score)), 2)


def _update_session_affective_state(
    db: Session,
    session_id: UUID,
    learner_id: int,
    score: float
) -> Dict[str, Any]:
    """
    Mettre à jour l'état affectif basé sur la performance de la session.
    
    Args:
        db: Session de base de données
        session_id: ID de la session
        learner_id: ID de l'apprenant
        score: Score final de la session
    
    Returns:
        État affectif mis à jour
    """
    # Récupérer le dernier état affectif (si existe)
    latest = get_latest_affective_state(db, session_id)
    
    if latest:
        # Mettre à jour basé sur l'état précédent
        motivation, frustration, confidence, stress = update_affective_state(
            latest.motivation_level or 0.5,
            latest.frustration_level or 0.0,
            latest.confidence_level or 0.5,
            latest.stress_level or 0.0,
            score
        )
    else:
        # Créer un état initial basé sur le score
        motivation, frustration, confidence, stress = update_affective_state(
            0.5, 0.0, 0.5, 0.0, score
        )
    
    # Enregistrer le nouvel état
    new_affective = record_affective_state(
        db,
        session_id,
        stress,
        confidence,
        motivation,
        frustration
    )
    
    return {
        "motivation": motivation,
        "frustration": frustration,
        "confidence": confidence,
        "stress": stress,
        "label": get_affective_label(motivation, frustration, confidence, stress)
    }


def _update_learner_behavior(
    db: Session,
    learner_id: int,
    session_time: int
) -> None:
    """
    Mettre à jour le profil comportemental de l'apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        session_time: Temps de la session en secondes
    """
    from app.services.behavior_service import compute_engagement
    
    # Récupérer ou créer le profil comportemental
    behavior = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == learner_id
    ).first()
    
    if not behavior:
        behavior = LearnerBehavior(
            learner_id=learner_id,
            sessions_count=0,
            activities_count=0,
            total_time_spent=0
        )
        db.add(behavior)
    
    # Mettre à jour les compteurs
    behavior.sessions_count = (behavior.sessions_count or 0) + 1
    behavior.activities_count = (behavior.activities_count or 0) + 1  # Une session = une activité
    behavior.total_time_spent = (behavior.total_time_spent or 0) + session_time
    
    # Recalculer le score d'engagement
    behavior.engagement_score = compute_engagement(
        behavior.sessions_count,
        behavior.activities_count,
        behavior.total_time_spent
    )
    
    db.commit()


def _generate_pedagogical_recommendation(
    db: Session,
    learner_id: int,
    score: float,
    masteries: List[Dict],
    affective: Dict
) -> str:
    """
    Générer une recommandation pédagogique personnalisée.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        score: Score obtenu
        masteries: Maîtrises de compétences
        affective: État affectif
    
    Returns:
        Recommandation textuelle
    """
    # Calculer le niveau moyen de maîtrise
    if masteries:
        avg_mastery = sum(m["mastery_level"] for m in masteries) / len(masteries)
    else:
        avg_mastery = 0.5
    
    # Récupérer l'état affectif
    frustration = affective.get("frustration", 0.0)
    motivation = affective.get("motivation", 0.5)
    confidence = affective.get("confidence", 0.5)
    
    # Décision pédagogique basée sur le score et l'état
    if score < 40:
        if frustration > 0.7:
            return "Score faible avec forte frustration. Recommandation : Revoir les concepts de base avec des cas très guidés et beaucoup d'encouragements. Prendre une pause si nécessaire."
        else:
            return "Score faible. Recommandation : Reprendre les fondamentaux avec des cas de niveau 1 et un tutorat renforcé."
    
    elif score < 60:
        if avg_mastery < 0.4:
            return "Score moyen avec maîtrise faible. Recommandation : Se concentrer sur les compétences faibles identifiées avec des exercices ciblés."
        else:
            return "Score moyen. Recommandation : Continuer à pratiquer sur des cas de même niveau pour consolider les acquis."
    
    elif score < 80:
        if confidence < 0.5:
            return "Bon score mais confiance faible. Recommandation : Renforcer la confiance avec plus de pratique sur le même niveau avant de progresser."
        else:
            return "Bonne performance ! Recommandation : Prêt pour des cas légèrement plus complexes. Continuer sur cette dynamique."
    
    else:  # score >= 80
        if avg_mastery >= 0.8 and motivation > 0.7:
            return "Excellente performance avec forte maîtrise ! Recommandation : Passer au niveau supérieur et explorer des cas plus complexes ou des spécialisations."
        else:
            return "Excellente performance ! Recommandation : Consolider cette maîtrise avec quelques cas similaires puis progresser vers le niveau suivant."


def _get_next_action(
    score: float,
    masteries: List[Dict],
    affective: Dict
) -> Dict[str, Any]:
    """
    Déterminer la prochaine action recommandée pour l'apprenant.
    
    Args:
        score: Score obtenu
        masteries: Maîtrises de compétences
        affective: État affectif
    
    Returns:
        Dictionnaire avec l'action suivante
    """
    # Calculer le niveau moyen de maîtrise
    if masteries:
        avg_mastery = sum(m["mastery_level"] for m in masteries) / len(masteries)
    else:
        avg_mastery = 0.5
    
    frustration = affective.get("frustration", 0.0)
    motivation = affective.get("motivation", 0.5)
    confidence = affective.get("confidence", 0.5)
    
    # Déterminer le niveau de difficulté recommandé
    if score < 40 or frustration > 0.7:
        difficulty = 1
        action_type = "revise_fundamentals"
        message = "Reprendre les bases avec des cas simples et guidés"
    elif score < 60 or avg_mastery < 0.4:
        difficulty = max(1, int(avg_mastery * 5))
        action_type = "practice_current_level"
        message = "Continuer à pratiquer au niveau actuel pour consolider"
    elif score < 80:
        if confidence < 0.5:
            difficulty = max(1, int(avg_mastery * 5))
            action_type = "build_confidence"
            message = "Renforcer la confiance au niveau actuel"
        else:
            difficulty = min(5, int(avg_mastery * 5) + 1)
            action_type = "progress_next_level"
            message = "Progresser vers des cas légèrement plus complexes"
    else:
        if avg_mastery >= 0.8 and motivation > 0.7:
            difficulty = min(5, int(avg_mastery * 5) + 1)
            action_type = "challenge"
            message = "Relever des défis plus complexes"
        else:
            difficulty = int(avg_mastery * 5)
            action_type = "consolidate"
            message = "Consolider les acquis avant de progresser"
    
    return {
        "action_type": action_type,
        "recommended_difficulty": difficulty,
        "message": message,
        "estimated_duration_min": 20 + (difficulty * 10),
        "support_level": "high" if frustration > 0.5 else "medium" if confidence < 0.5 else "low"
    }


def get_adaptation_summary(
    db: Session,
    learner_id: int
) -> Dict[str, Any]:
    """
    Obtenir un résumé complet de l'adaptation pour un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Résumé complet incluant tous les modèles
    """
    from app.services.knowledge_inference_service import get_learner_knowledge_summary
    from app.services.performance_service import get_learner_performance_stats
    from app.services.behavior_service import get_behavior_profile
    
    # 1. Modèle de connaissances
    knowledge = get_learner_knowledge_summary(db, learner_id)
    
    # 2. Modèle de performances
    performance = get_learner_performance_stats(db, learner_id)
    
    # 3. Modèle comportemental
    behavior = db.query(LearnerBehavior).filter(
        LearnerBehavior.learner_id == learner_id
    ).first()
    
    if behavior:
        behavior_profile = get_behavior_profile(
            behavior.sessions_count or 0,
            behavior.activities_count or 0,
            behavior.total_time_spent or 0
        )
    else:
        behavior_profile = {
            "engagement_score": 0.0,
            "engagement_label": "Non évalué",
            "sessions": 0,
            "activities": 0
        }
    
    # 4. État affectif (dernière session)
    latest_session = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id
    ).order_by(SimulationSession.start_time.desc()).first()
    
    if latest_session:
        latest_affective = get_latest_affective_state(db, latest_session.id)
        if latest_affective:
            affective_state = {
                "motivation": latest_affective.motivation_level,
                "frustration": latest_affective.frustration_level,
                "confidence": latest_affective.confidence_level,
                "stress": latest_affective.stress_level,
                "label": get_affective_label(
                    latest_affective.motivation_level or 0.5,
                    latest_affective.frustration_level or 0.0,
                    latest_affective.confidence_level or 0.5,
                    latest_affective.stress_level or 0.0
                )
            }
        else:
            affective_state = {"label": "Non évalué"}
    else:
        affective_state = {"label": "Aucune session"}
    
    # 5. Statut global et recommandation
    overall_status = _determine_overall_status(
        knowledge.get("average_mastery", 0),
        performance.get("average_score", 0),
        behavior_profile.get("engagement_score", 0)
    )
    
    return {
        "learner_id": learner_id,
        "knowledge_model": knowledge,
        "performance_model": performance,
        "behavioral_model": behavior_profile,
        "affective_state": affective_state,
        "overall_status": overall_status,
        "generated_at": func.now()
    }


def _determine_overall_status(
    avg_mastery: float,
    avg_score: float,
    engagement: float
) -> Dict[str, Any]:
    """
    Déterminer le statut global de l'apprenant.
    
    Args:
        avg_mastery: Maîtrise moyenne
        avg_score: Score moyen
        engagement: Score d'engagement
    
    Returns:
        Statut global avec niveau et description
    """
    # Score composite
    composite_score = (avg_mastery * 0.4) + (avg_score / 100 * 0.4) + (engagement * 0.2)
    
    if composite_score >= 0.8:
        level = "excellent"
        description = "Performance excellente sur tous les axes"
    elif composite_score >= 0.6:
        level = "good"
        description = "Bonne progression générale"
    elif composite_score >= 0.4:
        level = "moderate"
        description = "Progression modérée, nécessite plus de pratique"
    else:
        level = "needs_improvement"
        description = "Nécessite un accompagnement renforcé"
    
    return {
        "level": level,
        "composite_score": round(composite_score, 2),
        "description": description
    }