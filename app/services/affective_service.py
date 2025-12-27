"""Service de gestion de l'état affectif de l'apprenant."""
from typing import Tuple
from sqlalchemy.orm import Session
from app.models.learner_affective import LearnerAffectiveState


def update_affective_state(
    motivation: float,
    frustration: float,
    confidence: float,
    stress: float,
    score: float,
    previous_score: float = None
) -> Tuple[float, float, float, float]:
    """
    Mise à jour de l'état affectif basée sur la performance.
    
    Args:
        motivation: Motivation actuelle (0-1)
        frustration: Frustration actuelle (0-1)
        confidence: Confiance actuelle (0-1)
        stress: Stress actuel (0-1)
        score: Score obtenu (0-100)
        previous_score: Score précédent (optionnel)
    
    Returns:
        Tuple (motivation, frustration, confidence, stress) mis à jour
    """
    # Normaliser le score (0-100 → 0-1)
    normalized_score = score / 100.0
    
    # Cas 1: Mauvaise performance (score < 50)
    if score < 50:
        # Augmenter la frustration
        frustration = min(1.0, frustration + 0.15)
        # Diminuer la confiance
        confidence = max(0.0, confidence - 0.15)
        # Augmenter le stress
        stress = min(1.0, stress + 0.1)
        # Diminuer la motivation
        motivation = max(0.0, motivation - 0.1)
    
    # Cas 2: Performance moyenne (50-70)
    elif score < 70:
        frustration = max(0.0, frustration - 0.05)
        confidence = max(0.0, confidence - 0.05)
        stress = max(0.0, stress - 0.05)
        motivation = min(1.0, motivation + 0.05)
    
    # Cas 3: Bonne performance (70-85)
    elif score < 85:
        motivation = min(1.0, motivation + 0.15)
        frustration = max(0.0, frustration - 0.1)
        confidence = min(1.0, confidence + 0.1)
        stress = max(0.0, stress - 0.1)
    
    # Cas 4: Excellente performance (≥ 85)
    else:
        motivation = min(1.0, motivation + 0.2)
        frustration = max(0.0, frustration - 0.15)
        confidence = min(1.0, confidence + 0.2)
        stress = max(0.0, stress - 0.15)
    
    # Ajustement basé sur la progression
    if previous_score is not None:
        progress = score - previous_score
        
        if progress > 10:  # Progression significative
            motivation = min(1.0, motivation + 0.1)
            confidence = min(1.0, confidence + 0.1)
        elif progress < -10:  # Régression significative
            frustration = min(1.0, frustration + 0.1)
            confidence = max(0.0, confidence - 0.1)
    
    return (
        round(motivation, 2),
        round(frustration, 2),
        round(confidence, 2),
        round(stress, 2)
    )


def get_affective_label(
    motivation: float,
    frustration: float,
    confidence: float,
    stress: float
) -> str:
    """
    Obtenir un label descriptif de l'état affectif global.
    
    Args:
        motivation: Motivation (0-1)
        frustration: Frustration (0-1)
        confidence: Confiance (0-1)
        stress: Stress (0-1)
    
    Returns:
        Label descriptif
    """
    # Calculer un score affectif global
    positive_score = (motivation + confidence) / 2
    negative_score = (frustration + stress) / 2
    
    affective_balance = positive_score - negative_score
    
    if affective_balance > 0.3:
        return "Très positif"
    elif affective_balance > 0.1:
        return "Positif"
    elif affective_balance > -0.1:
        return "Neutre"
    elif affective_balance > -0.3:
        return "Négatif"
    else:
        return "Très négatif"


def detect_frustration(frustration: float, threshold: float = 0.7) -> bool:
    """
    Détecter si l'apprenant est frustré.
    
    Args:
        frustration: Niveau de frustration (0-1)
        threshold: Seuil de frustration (défaut: 0.7)
    
    Returns:
        True si frustré, False sinon
    """
    return frustration >= threshold


def detect_demotivation(motivation: float, threshold: float = 0.3) -> bool:
    """
    Détecter si l'apprenant est démotivé.
    
    Args:
        motivation: Niveau de motivation (0-1)
        threshold: Seuil de démotivation (défaut: 0.3)
    
    Returns:
        True si démotivé, False sinon
    """
    return motivation <= threshold


def get_feedback_type(
    motivation: float,
    frustration: float,
    confidence: float,
    stress: float
) -> str:
    """
    Déterminer le type de feedback à fournir.
    
    Args:
        motivation: Motivation (0-1)
        frustration: Frustration (0-1)
        confidence: Confiance (0-1)
        stress: Stress (0-1)
    
    Returns:
        Type de feedback: "encouragement", "aide", "challenge", "soutien"
    """
    is_frustrated = detect_frustration(frustration)
    is_demotivated = detect_demotivation(motivation)
    is_confident = confidence > 0.7
    is_stressed = stress > 0.7
    
    # Apprenant frustré → feedback guidé et encourageant
    if is_frustrated:
        return "soutien"
    
    # Apprenant démotivé → feedback encourageant
    if is_demotivated:
        return "encouragement"
    
    # Apprenant confiant et non stressé → feedback challenge
    if is_confident and not is_stressed:
        return "challenge"
    
    # Apprenant stressé → feedback rassurant
    if is_stressed:
        return "soutien"
    
    # Par défaut → feedback équilibré
    return "aide"


def get_affective_recommendations(
    motivation: float,
    frustration: float,
    confidence: float,
    stress: float
) -> list[str]:
    """
    Générer des recommandations basées sur l'état affectif.
    
    Args:
        motivation: Motivation (0-1)
        frustration: Frustration (0-1)
        confidence: Confiance (0-1)
        stress: Stress (0-1)
    
    Returns:
        Liste de recommandations
    """
    recommendations = []
    
    # Frustration
    if frustration > 0.7:
        recommendations.append("L'apprenant est très frustré. Proposer une aide immédiate.")
    elif frustration > 0.5:
        recommendations.append("L'apprenant montre des signes de frustration. Réduire la difficulté.")
    
    # Motivation
    if motivation < 0.3:
        recommendations.append("L'apprenant est démotivé. Proposer des activités plus engageantes.")
    elif motivation < 0.5:
        recommendations.append("La motivation est faible. Augmenter les encouragements.")
    
    # Confiance
    if confidence < 0.3:
        recommendations.append("L'apprenant manque de confiance. Proposer des activités plus faciles.")
    elif confidence > 0.8:
        recommendations.append("L'apprenant est confiant. Augmenter la difficulté progressivement.")
    
    # Stress
    if stress > 0.7:
        recommendations.append("L'apprenant est très stressé. Réduire la pression et proposer du soutien.")
    elif stress > 0.5:
        recommendations.append("L'apprenant montre des signes de stress. Ralentir le rythme.")
    
    if not recommendations:
        recommendations.append("L'apprenant semble en bon équilibre affectif. Maintenir le rythme actuel.")
    
    return recommendations


def get_affective_profile(
    motivation: float,
    frustration: float,
    confidence: float,
    stress: float
) -> dict:
    """
    Obtenir un profil affectif complet.
    
    Args:
        motivation: Motivation (0-1)
        frustration: Frustration (0-1)
        confidence: Confiance (0-1)
        stress: Stress (0-1)
    
    Returns:
        Dictionnaire avec profil affectif complet
    """
    return {
        "motivation": motivation,
        "frustration": frustration,
        "confidence": confidence,
        "stress": stress,
        "affective_label": get_affective_label(motivation, frustration, confidence, stress),
        "is_frustrated": detect_frustration(frustration),
        "is_demotivated": detect_demotivation(motivation),
        "feedback_type": get_feedback_type(motivation, frustration, confidence, stress),
        "recommendations": get_affective_recommendations(motivation, frustration, confidence, stress)
    }
