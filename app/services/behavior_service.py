"""Service d'analyse du comportement de l'apprenant."""


def compute_engagement(
    sessions: int,
    activities: int,
    time_spent: int
) -> float:
    """
    Calcul du score d'engagement.
    
    Formule pondérée:
    - Sessions: 30% (fréquence de connexion)
    - Activités: 40% (nombre d'activités réalisées)
    - Temps: 30% (temps total passé)
    
    Args:
        sessions: Nombre de sessions
        activities: Nombre d'activités réalisées
        time_spent: Temps total en secondes
    
    Returns:
        Score d'engagement (0.0 à 1.0)
    """
    # Normaliser les valeurs
    sessions_score = min(sessions / 20, 1.0)  # Max 20 sessions
    activities_score = min(activities / 50, 1.0)  # Max 50 activités
    time_score = min(time_spent / 36000, 1.0)  # Max 10 heures
    
    # Calcul pondéré
    engagement = (sessions_score * 0.3) + (activities_score * 0.4) + (time_score * 0.3)
    
    return min(1.0, max(0.0, engagement))


def get_engagement_label(engagement_score: float) -> str:
    """
    Obtenir un label textuel pour le score d'engagement.
    
    Args:
        engagement_score: Score d'engagement (0.0 à 1.0)
    
    Returns:
        Label descriptif
    """
    if engagement_score >= 0.8:
        return "Très engagé"
    elif engagement_score >= 0.6:
        return "Engagé"
    elif engagement_score >= 0.4:
        return "Modérément engagé"
    elif engagement_score >= 0.2:
        return "Peu engagé"
    else:
        return "Désengagé"


def compute_activity_rate(activities: int, sessions: int) -> float:
    """
    Calcul du taux d'activité par session.
    
    Args:
        activities: Nombre d'activités réalisées
        sessions: Nombre de sessions
    
    Returns:
        Nombre moyen d'activités par session
    """
    if sessions == 0:
        return 0.0
    
    return activities / sessions


def detect_disengagement(
    sessions: int,
    activities: int,
    time_spent: int,
    threshold: float = 0.3
) -> bool:
    """
    Détecter si l'apprenant est désengagé.
    
    Args:
        sessions: Nombre de sessions
        activities: Nombre d'activités
        time_spent: Temps total en secondes
        threshold: Seuil d'engagement (défaut: 0.3)
    
    Returns:
        True si désengagé, False sinon
    """
    engagement = compute_engagement(sessions, activities, time_spent)
    return engagement < threshold


def compute_consistency(activity_times: list[int]) -> float:
    """
    Mesurer la cohérence/régularité de l'engagement.
    
    Utilise l'écart-type normalisé.
    
    Args:
        activity_times: Liste des temps passés par activité
    
    Returns:
        Score de cohérence (0.0 à 1.0)
    """
    if len(activity_times) < 2:
        return 1.0
    
    mean_time = sum(activity_times) / len(activity_times)
    
    if mean_time == 0:
        return 0.0
    
    # Calcul de l'écart-type
    variance = sum((t - mean_time) ** 2 for t in activity_times) / len(activity_times)
    std_dev = variance ** 0.5
    
    # Coefficient de variation normalisé
    cv = std_dev / mean_time
    
    # Convertir en score (moins de variation = plus de cohérence)
    consistency = 1.0 / (1.0 + cv)
    
    return min(1.0, max(0.0, consistency))


def get_behavior_profile(
    sessions: int,
    activities: int,
    time_spent: int,
    activity_times: list[int] = None
) -> dict:
    """
    Obtenir un profil comportemental complet.
    
    Args:
        sessions: Nombre de sessions
        activities: Nombre d'activités
        time_spent: Temps total en secondes
        activity_times: Liste optionnelle des temps par activité
    
    Returns:
        Dictionnaire avec profil comportemental
    """
    engagement = compute_engagement(sessions, activities, time_spent)
    activity_rate = compute_activity_rate(activities, sessions)
    is_disengaged = detect_disengagement(sessions, activities, time_spent)
    consistency = compute_consistency(activity_times) if activity_times else 0.5
    
    return {
        "engagement_score": round(engagement, 2),
        "engagement_label": get_engagement_label(engagement),
        "sessions": sessions,
        "activities": activities,
        "total_time_spent": time_spent,
        "average_time_per_activity": round(time_spent / activities, 2) if activities > 0 else 0,
        "activity_rate": round(activity_rate, 2),
        "is_disengaged": is_disengaged,
        "consistency": round(consistency, 2),
        "recommendations": _get_recommendations(engagement, activity_rate, consistency)
    }


def _get_recommendations(engagement: float, activity_rate: float, consistency: float) -> list[str]:
    """
    Générer des recommandations basées sur le profil comportemental.
    
    Args:
        engagement: Score d'engagement
        activity_rate: Taux d'activité par session
        consistency: Score de cohérence
    
    Returns:
        Liste de recommandations
    """
    recommendations = []
    
    if engagement < 0.3:
        recommendations.append("L'apprenant est désengagé. Envisager une intervention pédagogique.")
    elif engagement < 0.5:
        recommendations.append("L'engagement est faible. Proposer des activités plus motivantes.")
    
    if activity_rate < 1.0:
        recommendations.append("Le taux d'activité est faible. Encourager plus d'activités par session.")
    
    if consistency < 0.5:
        recommendations.append("L'engagement est irrégulier. Établir une routine d'apprentissage.")
    
    if not recommendations:
        recommendations.append("L'apprenant montre un bon engagement et une bonne cohérence.")
    
    return recommendations
