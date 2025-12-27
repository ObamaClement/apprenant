"""Schémas Pydantic pour les performances de l'apprenant."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LearnerPerformanceBase(BaseModel):
    """Schéma de base pour les performances."""
    learner_id: int
    concept_id: int
    activity_type: str
    score: float = Field(ge=0.0, le=100.0)
    time_spent: Optional[int] = None
    attempts: int = Field(default=1, ge=1)


class LearnerPerformanceCreate(LearnerPerformanceBase):
    """Schéma pour créer un enregistrement de performance."""
    pass


class LearnerPerformanceResponse(LearnerPerformanceBase):
    """Schéma de réponse pour les performances."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
