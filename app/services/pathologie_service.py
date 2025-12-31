"""Service pour les pathologies."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.pathologie import Pathologie


def get_all_pathologies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    categorie: Optional[str] = None
) -> List[Pathologie]:
    """
    Récupérer toutes les pathologies avec filtres.
    
    Args:
        db: Session de base de données
        skip: Nombre de résultats à sauter
        limit: Nombre maximum de résultats
        categorie: Filtrer par catégorie
    
    Returns:
        Liste des pathologies
    """
    query = db.query(Pathologie)
    
    if categorie:
        query = query.filter(Pathologie.categorie == categorie)
    
    return query.offset(skip).limit(limit).all()


def get_pathologie_by_id(db: Session, pathologie_id: int) -> Optional[Pathologie]:
    """
    Récupérer une pathologie par ID.
    
    Args:
        db: Session de base de données
        pathologie_id: ID de la pathologie
    
    Returns:
        Pathologie ou None
    """
    return db.query(Pathologie).filter(Pathologie.id == pathologie_id).first()


def get_pathologie_by_icd10(db: Session, code_icd10: str) -> Optional[Pathologie]:
    """
    Récupérer une pathologie par code ICD10.
    
    Args:
        db: Session de base de données
        code_icd10: Code ICD10
    
    Returns:
        Pathologie ou None
    """
    return db.query(Pathologie).filter(Pathologie.code_icd10 == code_icd10).first()


def search_pathologies(
    db: Session,
    search_term: str,
    limit: int = 20
) -> List[Pathologie]:
    """
    Rechercher des pathologies par nom.
    
    Args:
        db: Session de base de données
        search_term: Terme de recherche
        limit: Nombre maximum de résultats
    
    Returns:
        Liste des pathologies trouvées
    """
    search_pattern = f"%{search_term}%"
    return db.query(Pathologie).filter(
        Pathologie.nom_fr.ilike(search_pattern)
    ).limit(limit).all()


def get_pathologies_by_gravite(
    db: Session,
    niveau_min: int,
    niveau_max: int = 5
) -> List[Pathologie]:
    """
    Récupérer les pathologies par niveau de gravité.
    
    Args:
        db: Session de base de données
        niveau_min: Niveau minimum de gravité
        niveau_max: Niveau maximum de gravité
    
    Returns:
        Liste des pathologies
    """
    return db.query(Pathologie).filter(
        Pathologie.niveau_gravite >= niveau_min,
        Pathologie.niveau_gravite <= niveau_max
    ).all()