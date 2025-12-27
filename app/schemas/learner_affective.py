"""Schémas Pydantic pour l'état affectif de l'apprenant."""
from pydantic import BaseModel, Field
from datetime import datetime


class LearnerAffectiveBase(BaseModel):
    """Schéma de base pour l'état affectif."""
    learner_id: int
    motivation: float = Field(default=0.5, ge=0.0, le=1.0)
    frustration: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    stress: float = Field(default=0.0, ge=0.0, le=1.0)


class LearnerAffectiveCreate(LearnerAffectiveBase):
    """Schéma pour créer un état affectif."""
    pass


class LearnerAffectiveResponse(LearnerAffectiveBase):
    """Schéma de réponse pour l'état affectif."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
