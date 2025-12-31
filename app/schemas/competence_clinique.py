"""Schémas Pydantic pour les compétences cliniques."""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class CompetenceCliniqueBase(BaseModel):
    """Schéma de base pour une compétence clinique."""
    code_competence: str
    nom: str
    categorie: Optional[str] = None
    niveau_bloom: Optional[int] = None
    description: Optional[str] = None
    objectifs_apprentissage: Optional[Dict[str, Any]] = None
    criteres_maitrise: Optional[Dict[str, Any]] = None
    parent_competence_id: Optional[int] = None
    ordre_apprentissage: Optional[int] = None


class CompetenceCliniqueCreate(CompetenceCliniqueBase):
    """Schéma pour créer une compétence clinique."""
    pass


class CompetenceCliniqueUpdate(BaseModel):
    """Schéma pour mettre à jour une compétence clinique."""
    nom: Optional[str] = None
    categorie: Optional[str] = None
    niveau_bloom: Optional[int] = None
    description: Optional[str] = None
    objectifs_apprentissage: Optional[Dict[str, Any]] = None
    criteres_maitrise: Optional[Dict[str, Any]] = None
    parent_competence_id: Optional[int] = None
    ordre_apprentissage: Optional[int] = None


class CompetenceCliniqueResponse(CompetenceCliniqueBase):
    """Schéma de réponse pour une compétence clinique."""
    id: int
    created_at: datetime
    
    # Propriétés de compatibilité avec Concept
    @property
    def name(self) -> str:
        return self.code_competence
    
    @property
    def p_init(self) -> float:
        return 0.2
    
    @property
    def p_transit(self) -> float:
        return 0.15
    
    @property
    def p_guess(self) -> float:
        return 0.2
    
    @property
    def p_slip(self) -> float:
        return 0.1

    class Config:
        from_attributes = True


# Schéma enrichi avec prérequis
class CompetenceCliniqueWithPrerequisResponse(CompetenceCliniqueResponse):
    """Schéma enrichi avec les prérequis."""
    prerequis_ids: Optional[List[int]] = []
    
    class Config:
        from_attributes = True