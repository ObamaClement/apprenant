"""Service d'analyse des performances basé sur SimulationSession."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.simulation_session import SimulationSession
from app.models.cas_clinique import CasCliniqueEnrichi


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


def performance_indicator(score: float) -> str:
    """
    Indicateur qualitatif de performance.
    
    Args:
        score: Score obtenu (0-100)
    
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
    learner_id: int
) -> Dict[str, Any]:
    """
    Obtenir les statistiques de performance d'un apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire avec statistiques
    """
    # Récupérer toutes les sessions terminées
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id,
        SimulationSession.statut == "termine"
    ).order_by(SimulationSession.start_time).all()
    
    if not sessions:
        return {
            "learner_id": learner_id,
            "total_sessions": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "worst_score": 0.0,
            "trend": "stable",
            "total_time_spent": 0,
            "sessions": []
        }
    
    scores = [s.score_final for s in sessions if s.score_final is not None]
    times = [s.temps_total for s in sessions if s.temps_total]
    
    return {
        "learner_id": learner_id,
        "total_sessions": len(sessions),
        "completed_sessions": len(sessions),
        "average_score": round(compute_average_score(scores), 2),
        "best_score": max(scores) if scores else 0.0,
        "worst_score": min(scores) if scores else 0.0,
        "progress": round(compute_progress(scores), 2),
        "trend": compute_trend(scores),
        "total_time_spent": sum(times) if times else 0,
        "average_time_per_session": round(sum(times) / len(times), 2) if times else 0,
        "sessions": [
            {
                "id": str(s.id),
                "cas_clinique_id": s.cas_clinique_id,
                "score": s.score_final,
                "indicator": performance_indicator(s.score_final) if s.score_final else "N/A",
                "temps_total": s.temps_total,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "raison_fin": s.raison_fin
            }
            for s in sessions
        ]
    }


def get_performance_by_difficulty(
    db: Session,
    learner_id: int
) -> Dict[int, Dict[str, Any]]:
    """
    Obtenir les performances par niveau de difficulté.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Dictionnaire {niveau_difficulte: statistiques}
    """
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id,
        SimulationSession.statut == "termine"
    ).all()
    
    # Grouper par niveau de difficulté
    by_difficulty = {}
    
    for session in sessions:
        case = db.query(CasCliniqueEnrichi).filter(
            CasCliniqueEnrichi.id == session.cas_clinique_id
        ).first()
        
        if not case or not case.niveau_difficulte:
            continue
        
        level = case.niveau_difficulte
        
        if level not in by_difficulty:
            by_difficulty[level] = {
                "sessions": [],
                "scores": []
            }
        
        by_difficulty[level]["sessions"].append(session)
        if session.score_final is not None:
            by_difficulty[level]["scores"].append(session.score_final)
    
    # Calculer les statistiques par niveau
    stats = {}
    for level, data in by_difficulty.items():
        scores = data["scores"]
        stats[level] = {
            "niveau_difficulte": level,
            "nb_sessions": len(data["sessions"]),
            "average_score": round(compute_average_score(scores), 2),
            "best_score": max(scores) if scores else 0.0,
            "success_rate": len([s for s in scores if s >= 60]) / len(scores) * 100 if scores else 0.0
        }
    
    return stats


def identify_weak_cases(
    db: Session,
    learner_id: int,
    threshold: float = 60.0
) -> List[Dict[str, Any]]:
    """
    Identifier les cas où l'apprenant a eu des difficultés.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        threshold: Seuil de score (défaut: 60)
    
    Returns:
        Liste des cas difficiles
    """
    sessions = db.query(SimulationSession).filter(
        SimulationSession.learner_id == learner_id,
        SimulationSession.statut == "termine",
        SimulationSession.score_final < threshold
    ).all()
    
    weak_cases = []
    
    for session in sessions:
        case = db.query(CasCliniqueEnrichi).filter(
            CasCliniqueEnrichi.id == session.cas_clinique_id
        ).first()
        
        if case:
            weak_cases.append({
                "session_id": str(session.id),
                "cas_clinique_id": case.id,
                "code_fultang": case.code_fultang,
                "niveau_difficulte": case.niveau_difficulte,
                "score": session.score_final,
                "pathologie_id": case.pathologie_principale_id,
                "date": session.start_time.isoformat() if session.start_time else None
            })
    
    # Trier par score croissant
    weak_cases.sort(key=lambda x: x["score"])
    
    return weak_cases


def get_performance_summary(
    db: Session,
    learner_id: int
) -> Dict[str, Any]:
    """
    Obtenir un résumé complet des performances.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
    
    Returns:
        Résumé complet
    """
    general_stats = get_learner_performance_stats(db, learner_id)
    by_difficulty = get_performance_by_difficulty(db, learner_id)
    weak_cases = identify_weak_cases(db, learner_id)
    
    return {
        "general": general_stats,
        "by_difficulty": by_difficulty,
        "weak_cases": weak_cases[:5],  # Top 5 des cas difficiles
        "recommendations": _generate_recommendations(general_stats, by_difficulty, weak_cases)
    }


def _generate_recommendations(
    general_stats: Dict,
    by_difficulty: Dict,
    weak_cases: List
) -> List[str]:
    """
    Générer des recommandations basées sur les performances.
    
    Args:
        general_stats: Statistiques générales
        by_difficulty: Performances par difficulté
        weak_cases: Cas difficiles
    
    Returns:
        Liste de recommandations
    """
    recommendations = []
    
    avg_score = general_stats.get("average_score", 0)
    trend = general_stats.get("trend", "stable")
    
    # Recommandations basées sur le score moyen
    if avg_score < 50:
        recommendations.append("Score moyen faible. Revoir les fondamentaux et commencer par des cas plus simples.")
    elif avg_score < 70:
        recommendations.append("Performances moyennes. Continuer à pratiquer sur des cas variés.")
    else:
        recommendations.append("Bonnes performances. Prêt pour des cas plus complexes.")
    
    # Recommandations basées sur la tendance
    if trend == "declining":
        recommendations.append("Tendance à la baisse détectée. Faire une pause ou revoir les concepts de base.")
    elif trend == "improving":
        recommendations.append("Progression positive ! Continuer sur cette lancée.")
    
    # Recommandations basées sur les niveaux de difficulté
    if by_difficulty:
        levels_with_issues = [
            level for level, stats in by_difficulty.items()
            if stats["average_score"] < 60
        ]
        if levels_with_issues:
            recommendations.append(
                f"Difficultés sur les niveaux {', '.join(map(str, levels_with_issues))}. "
                "Concentrer les efforts sur ces niveaux."
            )
    
    # Recommandations basées sur les cas faibles
    if len(weak_cases) > 5:
        recommendations.append(
            f"Plusieurs cas difficiles identifiés ({len(weak_cases)}). "
            "Reprendre les cas échoués pour renforcer la maîtrise."
        )
    
    return recommendations