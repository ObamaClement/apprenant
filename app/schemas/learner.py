"""Schémas Pydantic pour les apprenants."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class LearnerBase(BaseModel):
    """Schéma de base pour un apprenant."""
    first_name: str
    last_name: str
    email: EmailStr
    level: Optional[str] = None
    field_of_study: Optional[str] = None


class LearnerCreate(LearnerBase):
    """Schéma pour créer un apprenant."""
    pass


class LearnerUpdate(BaseModel):
    """Schéma pour mettre à jour un apprenant."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    level: Optional[str] = None
    field_of_study: Optional[str] = None


class LearnerResponse(LearnerBase):
    """Schéma de réponse pour un apprenant."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True