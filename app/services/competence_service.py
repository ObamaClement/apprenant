"""Service pour les compétences cliniques."""
from sqlalchemy.orm import Session
from typing import List, Optional, Set
from app.models.competence_clinique import CompetenceClinique
from app.models.prerequis_competence import PrerequisCompetence


def get_all_competences(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    categorie: Optional[str] = None
) -> List[CompetenceClinique]:
    """
    Récupérer toutes les compétences avec filtres.
    
    Args:
        db: Session de base de données
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
        categorie: Filtrer par catégorie
    
    Returns:
        Liste des compétences
    """
    query = db.query(CompetenceClinique)
    
    if categorie:
        query = query.filter(CompetenceClinique.categorie == categorie)
    
    return query.order_by(CompetenceClinique.ordre_apprentissage).offset(skip).limit(limit).all()


def get_competence_by_id(db: Session, competence_id: int) -> Optional[CompetenceClinique]:
    """
    Récupérer une compétence par ID.
    
    Args:
        db: Session de base de données
        competence_id: ID de la compétence
    
    Returns:
        Compétence ou None
    """
    return db.query(CompetenceClinique).filter(CompetenceClinique.id == competence_id).first()


def get_competence_by_code(db: Session, code_competence: str) -> Optional[CompetenceClinique]:
    """
    Récupérer une compétence par code.
    
    Args:
        db: Session de base de données
        code_competence: Code de la compétence
    
    Returns:
        Compétence ou None
    """
    return db.query(CompetenceClinique).filter(
        CompetenceClinique.code_competence == code_competence
    ).first()


def get_prerequis_for_competence(
    db: Session,
    competence_id: int
) -> List[CompetenceClinique]:
    """
    Récupérer les prérequis d'une compétence.
    
    Args:
        db: Session de base de données
        competence_id: ID de la compétence
    
    Returns:
        Liste des compétences prérequises
    """
    prerequis_relations = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.competence_id == competence_id
    ).all()
    
    prerequis_ids = [rel.prerequis_id for rel in prerequis_relations]
    
    if not prerequis_ids:
        return []
    
    return db.query(CompetenceClinique).filter(
        CompetenceClinique.id.in_(prerequis_ids)
    ).all()


def get_competences_depending_on(
    db: Session,
    competence_id: int
) -> List[CompetenceClinique]:
    """
    Récupérer les compétences qui dépendent de cette compétence.
    
    Args:
        db: Session de base de données
        competence_id: ID de la compétence
    
    Returns:
        Liste des compétences dépendantes
    """
    dependent_relations = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.prerequis_id == competence_id
    ).all()
    
    dependent_ids = [rel.competence_id for rel in dependent_relations]
    
    if not dependent_ids:
        return []
    
    return db.query(CompetenceClinique).filter(
        CompetenceClinique.id.in_(dependent_ids)
    ).all()


def check_prerequisites_met(
    db: Session,
    competence_id: int,
    learner_id: int,
    threshold: float = 0.7
) -> bool:
    """
    Vérifier si un apprenant a les prérequis pour une compétence.
    
    Args:
        db: Session de base de données
        competence_id: ID de la compétence cible
        learner_id: ID de l'apprenant
        threshold: Seuil de maîtrise requis
    
    Returns:
        True si tous les prérequis sont maîtrisés
    """
    from app.models.learner_competency_mastery import LearnerCompetencyMastery
    
    prerequis = get_prerequis_for_competence(db, competence_id)
    
    if not prerequis:
        return True  # Pas de prérequis
    
    for prereq in prerequis:
        mastery = db.query(LearnerCompetencyMastery).filter(
            LearnerCompetencyMastery.learner_id == learner_id,
            LearnerCompetencyMastery.competence_id == prereq.id
        ).first()
        
        if not mastery or (mastery.mastery_level or 0) < threshold:
            return False
    
    return True


def get_learning_path(
    db: Session,
    target_competence_id: int
) -> List[CompetenceClinique]:
    """
    Construire un chemin d'apprentissage pour atteindre une compétence.
    
    Args:
        db: Session de base de données
        target_competence_id: ID de la compétence cible
    
    Returns:
        Liste ordonnée des compétences à maîtriser
    """
    visited: Set[int] = set()
    path: List[CompetenceClinique] = []
    
    def traverse(comp_id: int):
        if comp_id in visited:
            return
        
        visited.add(comp_id)
        
        # Récupérer les prérequis
        prerequis = get_prerequis_for_competence(db, comp_id)
        
        # Traverser récursivement les prérequis
        for prereq in prerequis:
            traverse(prereq.id)
        
        # Ajouter la compétence courante
        comp = get_competence_by_id(db, comp_id)
        if comp:
            path.append(comp)
    
    traverse(target_competence_id)
    return path