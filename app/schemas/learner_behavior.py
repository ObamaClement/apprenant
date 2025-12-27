"""Schémas Pydantic pour le comportement de l'apprenant."""
from pydantic import BaseModel, Field
from datetime import datetime


class LearnerBehaviorBase(BaseModel):
    """Schéma de base pour le comportement."""
    learner_id: int
    sessions_count: int = Field(ge=0)
    activities_count: int = Field(ge=0)
    total_time_spent: int = Field(ge=0)


class LearnerBehaviorCreate(LearnerBehaviorBase):
    """Schéma pour créer un enregistrement de comportement."""
    pass


class LearnerBehaviorResponse(LearnerBehaviorBase):
    """Schéma de réponse pour le comportement."""
    id: int
    engagement_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
