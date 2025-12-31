"""Schémas Pydantic pour l'état affectif de l'apprenant."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class LearnerAffectiveBase(BaseModel):
    """Schéma de base pour l'état affectif."""
    session_id: UUID
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    motivation_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    frustration_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class LearnerAffectiveCreate(LearnerAffectiveBase):
    """Schéma pour créer un état affectif."""
    pass


class LearnerAffectiveUpdate(BaseModel):
    """Schéma pour mettre à jour l'état affectif."""
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    motivation_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    frustration_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class LearnerAffectiveResponse(LearnerAffectiveBase):
    """Schéma de réponse pour l'état affectif."""
    id: int
    timestamp: datetime
    
    # Propriétés de compatibilité
    @property
    def stress(self) -> Optional[float]:
        return self.stress_level
    
    @property
    def confidence(self) -> Optional[float]:
        return self.confidence_level
    
    @property
    def motivation(self) -> Optional[float]:
        return self.motivation_level
    
    @property
    def frustration(self) -> Optional[float]:
        return self.frustration_level

    class Config:
        from_attributes = True