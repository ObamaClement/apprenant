"""Schémas Pydantic pour le profil cognitif de l'apprenant."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LearnerCognitiveBase(BaseModel):
    """Schéma de base pour le profil cognitif."""
    learner_id: int
    learning_style: Optional[str] = None
    learning_speed: Optional[float] = Field(None, ge=0.0, le=1.0)
    autonomy_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class LearnerCognitiveCreate(LearnerCognitiveBase):
    """Schéma pour créer un profil cognitif."""
    pass


class LearnerCognitiveResponse(LearnerCognitiveBase):
    """Schéma de réponse pour le profil cognitif."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
