"""Schémas Pydantic pour le comportement de l'apprenant."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LearnerBehaviorBase(BaseModel):
    """Schéma de base pour le comportement."""
    learner_id: int
    sessions_count: Optional[int] = Field(default=0, ge=0)
    activities_count: Optional[int] = Field(default=0, ge=0)
    total_time_spent: Optional[int] = Field(default=0, ge=0)


class LearnerBehaviorCreate(LearnerBehaviorBase):
    """Schéma pour créer un enregistrement de comportement."""
    pass


class LearnerBehaviorUpdate(BaseModel):
    """Schéma pour mettre à jour le comportement."""
    sessions_count: Optional[int] = Field(None, ge=0)
    activities_count: Optional[int] = Field(None, ge=0)
    total_time_spent: Optional[int] = Field(None, ge=0)


class LearnerBehaviorResponse(LearnerBehaviorBase):
    """Schéma de réponse pour le comportement."""
    id: int
    engagement_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True