"""Schémas Pydantic pour les apprenants."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class LearnerBase(BaseModel):
    """Schéma de base pour un apprenant."""
    matricule: Optional[str] = None
    nom: str
    email: EmailStr
    niveau_etudes: Optional[str] = None
    specialite_visee: Optional[str] = None
    langue_preferee: Optional[str] = "fr"


class LearnerCreate(LearnerBase):
    """Schéma pour créer un apprenant."""
    pass


class LearnerUpdate(BaseModel):
    """Schéma pour mettre à jour un apprenant."""
    matricule: Optional[str] = None
    nom: Optional[str] = None
    niveau_etudes: Optional[str] = None
    specialite_visee: Optional[str] = None
    langue_preferee: Optional[str] = None


class LearnerResponse(LearnerBase):
    """Schéma de réponse pour un apprenant."""
    id: int
    date_inscription: datetime
    
    # Propriétés de compatibilité
    @property
    def first_name(self) -> str:
        if self.nom:
            return self.nom.split()[0]
        return ""
    
    @property
    def last_name(self) -> str:
        if self.nom:
            parts = self.nom.split()
            return " ".join(parts[1:]) if len(parts) > 1 else ""
        return ""
    
    @property
    def level(self) -> Optional[str]:
        return self.niveau_etudes
    
    @property
    def field_of_study(self) -> Optional[str]:
        return self.specialite_visee
    
    @property
    def created_at(self) -> datetime:
        return self.date_inscription
    
    class Config:
        from_attributes = True