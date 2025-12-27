"""Service d'analyse des performances de l'apprenant."""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.learner_performance import LearnerPerformance
from app.models.concept import Concept


def compute_progress(scores: List[float]) -> float:
    """
    Calcul simple de la progression.
    
    Retourne la différence entre le dernier score et le premier.
    
    Args:
        scores: Liste des scores (0-100)
    
    Returns:
        Progression (peut être négative)
    """
    if len(scores) < 2:
        return 0.0
    
    return scores[-1] - scores[0]


def compute_average_score(scores: List[float]) -> float:
    """
    Calcul du score moyen.
    
    Args:
        scores: Liste des scores (0-100)
    
    Returns:
        Score moyen
    """
    if not scores:
        return 0.0
    
    return sum(scores) / len(scores)


def compute_trend(scores: List[float]) -> str:
    """
    Déterminer la tendance des performances.
    
    Args:
        scores: Liste des scores (0-100)
    
    Returns:
        "improving", "stable", ou "declining"
    """
    if len(scores) < 2:
        return "stable"
    
    # Comparer les 3 derniers scores avec les 3 premiers
    if len(scores) >= 3:
        recent_avg = sum(scores[-3:]) / 3
        earlier_avg = sum(scores[:3]) / 3
    else:
        recent_avg = scores[-1]
        earlier_avg = scores[0]
    
    difference = recent_avg - earlier_avg
    
    if difference > 5:
        return "improving"
    elif difference < -5:
        return "declining"
    else:
        return "stable"


def performance_indicator(score: float, time_spent: int = None) -> str:
    """
    Indicateur qualitatif de performance.
    
    Args:
        score: Score obtenu (0-100)
        time_spent: Temps passé en secondes (optionnel)
    
    Returns:
        Label: "excellent", "bon", "moyen", ou "faible"
    """
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "bon"
    elif score >= 40:
        return "moyen"
    else:
        return "faible"


def get_learner_performance_stats(
    db: Session,
    learner_id: int,
    concept_id: int = None
) -> dict:
    """
    Obtenir les statistiques de performance d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        concept_id: ID du concept (optionnel, pour filtrer)
    
    Returns:
        Dictionnaire avec statistiques
    """
    query = db.query(LearnerPerformance).filter(
        LearnerPerformance.learner_id == learner_id
    )
    
    if concept_id:
        query = query.filter(LearnerPerformance.concept_id == concept_id)
    
    performances = query.order_by(LearnerPerformance.created_at).all()
    
    if not performances:
        return {
            "learner_id": learner_id,
            "concept_id": concept_id,
            "total_activities": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "worst_score": 0.0,
            "trend": "stable",
            "total_time_spent": 0,
            "activities": []
        }
    
    scores = [p.score for p in performances]
    times = [p.time_spent for p in performances if p.time_spent]
    
    return {
        "learner_id": learner_id,
        "concept_id": concept_id,
        "total_activities": len(performances),
        "average_score": round(compute_average_score(scores), 2),
        "best_score": max(scores),
        "worst_score": min(scores),
        "progress": round(compute_progress(scores), 2),
        "trend": compute_trend(scores),
        "total_time_spent": sum(times) if times else 0,
        "average_time_per_activity": round(sum(times) / len(times), 2) if times else 0,
        "activities": [
            {
                "id": p.id,
                "activity_type": p.activity_type,
                "score": p.score,
                "indicator": performance_indicator(p.score, p.time_spent),
                "time_spent": p.time_spent,
                "attempts": p.attempts,
                "created_at": p.created_at.isoformat()
            }
            for p in performances
        ]
    }


def get_concept_performance_summary(
    db: Session,
    learner_id: int
) -> dict:
    """
    Obtenir un résumé des performances par concept.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire avec performances par concept
    """
    performances = db.query(LearnerPerformance).filter(
        LearnerPerformance.learner_id == learner_id
    ).all()
    
    if not performances:
        return {
            "learner_id": learner_id,
            "total_concepts": 0,
            "overall_average": 0.0,
            "concepts": []
        }
    
    # Grouper par concept
    concept_data = {}
    for perf in performances:
        if perf.concept_id not in concept_data:
            concept_data[perf.concept_id] = {
                "concept_id": perf.concept_id,
                "concept_name": perf.concept.name if perf.concept else "Unknown",
                "scores": [],
                "activities": 0
            }
        concept_data[perf.concept_id]["scores"].append(perf.score)
        concept_data[perf.concept_id]["activities"] += 1
    
    # Calculer les statistiques par concept
    concepts_summary = []
    all_scores = []
    
    for concept_id, data in concept_data.items():
        avg_score = compute_average_score(data["scores"])
        concepts_summary.append({
            "concept_id": concept_id,
            "concept_name": data["concept_name"],
            "average_score": round(avg_score, 2),
            "best_score": max(data["scores"]),
            "worst_score": min(data["scores"]),
            "activities": data["activities"],
            "trend": compute_trend(data["scores"]),
            "indicator": performance_indicator(avg_score)
        })
        all_scores.extend(data["scores"])
    
    # Trier par score moyen décroissant
    concepts_summary.sort(key=lambda x: x["average_score"], reverse=True)
    
    return {
        "learner_id": learner_id,
        "total_concepts": len(concepts_summary),
        "overall_average": round(compute_average_score(all_scores), 2),
        "concepts": concepts_summary
    }


def identify_weak_concepts(
    db: Session,
    learner_id: int,
    threshold: float = 60.0
) -> List[dict]:
    """
    Identifier les concepts où l'apprenant a des difficultés.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        threshold: Seuil de score pour considérer comme faible (défaut: 60)
    
    Returns:
        Liste des concepts faibles
    """
    summary = get_concept_performance_summary(db, learner_id)
    
    weak_concepts = [
        c for c in summary["concepts"]
        if c["average_score"] < threshold
    ]
    
    return weak_concepts
