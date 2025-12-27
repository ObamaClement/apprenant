"""Fonctions utilitaires pour les métriques."""
from typing import List


def calculate_average_score(scores: List[float]) -> float:
    """Calculer la moyenne des scores."""
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def calculate_success_rate(attempts: int, successes: int) -> float:
    """Calculer le taux de réussite."""
    if attempts == 0:
        return 0.0
    return (successes / attempts) * 100


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Normaliser un score entre 0 et 1."""
    if max_val == min_val:
        return 0.0
    return (score - min_val) / (max_val - min_val)


def calculate_engagement_level(interaction_count: int, time_spent: float) -> float:
    """Calculer le niveau d'engagement basé sur les interactions et le temps."""
    # Formule simple : engagement = (interactions * 0.6) + (time_spent * 0.4)
    # Normalisé entre 0 et 1
    engagement = (interaction_count * 0.6) + (time_spent * 0.4)
    return min(1.0, max(0.0, engagement))
