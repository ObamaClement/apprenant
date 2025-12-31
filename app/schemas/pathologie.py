"""Schémas Pydantic pour les pathologies."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class PathologieBase(BaseModel):
    """Schéma de base pour une pathologie."""
    code_icd10: Optional[str] = None
    nom_fr: str
    nom_en: Optional[str] = None
    nom_local: Optional[str] = None
    categorie: Optional[str] = None
    prevalence_cameroun: Optional[Decimal] = None
    niveau_gravite: Optional[int] = None
    description: Optional[str] = None


class PathologieCreate(PathologieBase):
    """Schéma pour créer une pathologie."""
    pass


class PathologieUpdate(BaseModel):
    """Schéma pour mettre à jour une pathologie."""
    nom_fr: Optional[str] = None
    nom_en: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    physiopathologie: Optional[str] = None


class PathologieResponse(PathologieBase):
    """Schéma de réponse pour une pathologie."""
    id: int
    physiopathologie: Optional[str] = None
    evolution_naturelle: Optional[str] = None
    complications: Optional[Dict[str, Any]] = None
    facteurs_risque: Optional[Dict[str, Any]] = None
    prevention: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schéma simplifié
class PathologieListResponse(BaseModel):
    """Schéma simplifié pour liste."""
    id: int
    code_icd10: Optional[str] = None
    nom_fr: str
    categorie: Optional[str] = None
    niveau_gravite: Optional[int] = None
    
    class Config:
        from_attributes = True