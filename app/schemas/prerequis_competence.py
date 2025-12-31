"""Schémas Pydantic pour les prérequis entre compétences."""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class PrerequisCompetenceBase(BaseModel):
    """Schéma de base pour un prérequis."""
    competence_id: int
    prerequis_id: int
    type_relation: Optional[str] = None
    force_relation: Optional[Decimal] = Field(None, ge=0.0, le=1.0)


class PrerequisCompetenceCreate(PrerequisCompetenceBase):
    """Schéma pour créer un prérequis."""
    pass


class PrerequisCompetenceUpdate(BaseModel):
    """Schéma pour mettre à jour un prérequis."""
    type_relation: Optional[str] = None
    force_relation: Optional[Decimal] = Field(None, ge=0.0, le=1.0)


class PrerequisCompetenceResponse(PrerequisCompetenceBase):
    """Schéma de réponse pour un prérequis."""
    id: int

    class Config:
        from_attributes = True


# Schéma enrichi avec noms des compétences
class PrerequisCompetenceWithNames(PrerequisCompetenceResponse):
    """Schéma enrichi avec les noms des compétences."""
    competence_code: Optional[str] = None
    competence_nom: Optional[str] = None
    prerequis_code: Optional[str] = None
    prerequis_nom: Optional[str] = None
    
    class Config:
        from_attributes = True