"""Schémas Pydantic pour l'historique d'apprentissage."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LearningHistoryBase(BaseModel):
    """Schéma de base pour l'historique d'apprentissage."""
    learner_id: int
    activity_type: str
    activity_ref: Optional[str] = None
    success: Optional[bool] = None
    score: Optional[int] = None
    time_spent: Optional[int] = None


class LearningHistoryCreate(LearningHistoryBase):
    """Schéma pour créer un enregistrement d'historique."""
    pass


class LearningHistoryResponse(LearningHistoryBase):
    """Schéma de réponse pour l'historique d'apprentissage."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
