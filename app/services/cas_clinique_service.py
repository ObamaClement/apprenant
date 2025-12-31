"""Service pour les cas cliniques."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.models.cas_clinique import CasCliniqueEnrichi
from app.models.pathologie import Pathologie


def get_all_cases(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    niveau_difficulte: Optional[int] = None,
    valide_expert: Optional[bool] = True
) -> List[CasCliniqueEnrichi]:
    """
    Récupérer tous les cas cliniques avec filtres.
    
    Args:
        db: Session de base de données
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
        niveau_difficulte: Filtrer par niveau (1-5)
        valide_expert: Filtrer par validation expert
    
    Returns:
        Liste des cas cliniques
    """
    query = db.query(CasCliniqueEnrichi)
    
    if niveau_difficulte is not None:
        query = query.filter(CasCliniqueEnrichi.niveau_difficulte == niveau_difficulte)
    
    if valide_expert is not None:
        query = query.filter(CasCliniqueEnrichi.valide_expert == valide_expert)
    
    return query.offset(skip).limit(limit).all()


def get_case_by_id(db: Session, cas_id: int) -> Optional[CasCliniqueEnrichi]:
    """
    Récupérer un cas clinique par ID.
    
    Args:
        db: Session de base de données
        cas_id: ID du cas clinique
    
    Returns:
        Cas clinique ou None
    """
    return db.query(CasCliniqueEnrichi).filter(CasCliniqueEnrichi.id == cas_id).first()


def get_case_by_code(db: Session, code_fultang: str) -> Optional[CasCliniqueEnrichi]:
    """
    Récupérer un cas clinique par son code.
    
    Args:
        db: Session de base de données
        code_fultang: Code du cas
    
    Returns:
        Cas clinique ou None
    """
    return db.query(CasCliniqueEnrichi).filter(
        CasCliniqueEnrichi.code_fultang == code_fultang
    ).first()


def get_cases_by_pathologie(
    db: Session,
    pathologie_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[CasCliniqueEnrichi]:
    """
    Récupérer les cas pour une pathologie donnée.
    
    Args:
        db: Session de base de données
        pathologie_id: ID de la pathologie
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
    
    Returns:
        Liste des cas cliniques
    """
    return db.query(CasCliniqueEnrichi).filter(
        CasCliniqueEnrichi.pathologie_principale_id == pathologie_id
    ).offset(skip).limit(limit).all()


def get_cases_by_competences(
    db: Session,
    competences_ids: List[int],
    skip: int = 0,
    limit: int = 50
) -> List[CasCliniqueEnrichi]:
    """
    Récupérer les cas qui sollicitent des compétences données.
    
    Args:
        db: Session de base de données
        competences_ids: Liste des IDs de compétences
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
    
    Returns:
        Liste des cas cliniques
    """
    # Les compétences sont stockées en JSON dans competences_requises
    cases = db.query(CasCliniqueEnrichi).filter(
        CasCliniqueEnrichi.competences_requises.isnot(None)
    ).offset(skip).limit(limit).all()
    
    # Filtrer en Python (car JSON)
    filtered = []
    for case in cases:
        if case.competences_requises and isinstance(case.competences_requises, dict):
            case_comp_ids = case.competences_requises.get('competence_ids', [])
            if any(comp_id in case_comp_ids for comp_id in competences_ids):
                filtered.append(case)
    
    return filtered


def increment_case_usage(db: Session, cas_id: int) -> None:
    """
    Incrémenter le compteur d'utilisation d'un cas.
    
    Args:
        db: Session de base de données
        cas_id: ID du cas clinique
    """
    case = db.query(CasCliniqueEnrichi).filter(CasCliniqueEnrichi.id == cas_id).first()
    if case:
        case.nb_utilisations = (case.nb_utilisations or 0) + 1
        db.commit()


def update_case_statistics(
    db: Session,
    cas_id: int,
    score: float,
    diagnostic_correct: bool
) -> None:
    """
    Mettre à jour les statistiques d'un cas (note moyenne, taux succès).
    
    Args:
        db: Session de base de données
        cas_id: ID du cas clinique
        score: Score obtenu (0-100)
        diagnostic_correct: Le diagnostic était-il correct ?
    """
    case = db.query(CasCliniqueEnrichi).filter(CasCliniqueEnrichi.id == cas_id).first()
    if not case:
        return
    
    # Mettre à jour la note moyenne
    if case.note_moyenne_apprenants is None:
        case.note_moyenne_apprenants = score / 100.0
    else:
        # Moyenne pondérée
        nb_uses = case.nb_utilisations or 1
        current_avg = float(case.note_moyenne_apprenants)
        case.note_moyenne_apprenants = (current_avg * (nb_uses - 1) + score / 100.0) / nb_uses
    
    # Mettre à jour le taux de succès diagnostic
    if case.taux_succes_diagnostic is None:
        case.taux_succes_diagnostic = 100.0 if diagnostic_correct else 0.0
    else:
        nb_uses = case.nb_utilisations or 1
        current_rate = float(case.taux_succes_diagnostic)
        success_increment = 100.0 if diagnostic_correct else 0.0
        case.taux_succes_diagnostic = (current_rate * (nb_uses - 1) + success_increment) / nb_uses
    
    db.commit()


def get_recommended_cases_for_learner(
    db: Session,
    learner_id: int,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Recommander des cas adaptés au niveau de l'apprenant.
    
    Args:
        db: Session de base de données
        learner_id: ID de l'apprenant
        limit: Nombre de cas à recommander
    
    Returns:
        Liste des cas recommandés avec scores de pertinence
    """
    # Récupérer les maîtrises de l'apprenant
    from app.models.learner_competency_mastery import LearnerCompetencyMastery
    
    masteries = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id
    ).all()
    
    # Calculer le niveau moyen de l'apprenant
    if masteries:
        avg_mastery = sum(m.mastery_level or 0 for m in masteries) / len(masteries)
    else:
        avg_mastery = 0.3  # Débutant par défaut
    
    # Déterminer le niveau de difficulté adapté
    if avg_mastery < 0.3:
        target_difficulty = 1
    elif avg_mastery < 0.5:
        target_difficulty = 2
    elif avg_mastery < 0.7:
        target_difficulty = 3
    elif avg_mastery < 0.85:
        target_difficulty = 4
    else:
        target_difficulty = 5
    
    # Récupérer les cas de ce niveau
    cases = db.query(CasCliniqueEnrichi).filter(
        CasCliniqueEnrichi.niveau_difficulte == target_difficulty,
        CasCliniqueEnrichi.valide_expert == True
    ).limit(limit * 2).all()  # Plus de cas pour filtrer
    
    # Scorer les cas
    recommendations = []
    for case in cases:
        score = 1.0
        
        # Bonus si peu utilisé (découverte)
        if (case.nb_utilisations or 0) < 5:
            score += 0.2
        
        # Bonus si bonne note moyenne
        if case.note_moyenne_apprenants and case.note_moyenne_apprenants > 0.7:
            score += 0.1
        
        recommendations.append({
            'case': case,
            'relevance_score': score,
            'reason': f"Adapté à votre niveau (difficulté {target_difficulty})"
        })
    
    # Trier par score et limiter
    recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
    return recommendations[:limit]