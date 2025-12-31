"""Schémas Pydantic pour les symptômes."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SymptomeBase(BaseModel):
    """Schéma de base pour un symptôme."""
    nom: str
    nom_local: Optional[str] = None
    categorie: Optional[str] = None
    type_symptome: Optional[str] = None
    description: Optional[str] = None
    questions_anamnese: Optional[Dict[str, Any]] = None
    signes_alarme: bool = False


class SymptomeCreate(SymptomeBase):
    """Schéma pour créer un symptôme."""
    pass


class SymptomeUpdate(BaseModel):
    """Schéma pour mettre à jour un symptôme."""
    nom_local: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    questions_anamnese: Optional[Dict[str, Any]] = None
    signes_alarme: Optional[bool] = None


class SymptomeResponse(SymptomeBase):
    """Schéma de réponse pour un symptôme."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True