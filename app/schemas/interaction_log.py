"""Schémas Pydantic pour les logs d'interaction."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class InteractionLogBase(BaseModel):
    """Schéma de base pour un log d'interaction."""
    session_id: UUID
    action_category: Optional[str] = None
    action_type: str
    action_content: Optional[Dict[str, Any]] = None
    response_latency: Optional[int] = Field(None, ge=0)
    charge_cognitive_estimee: Optional[float] = Field(None, ge=0.0, le=1.0)
    est_pertinent: Optional[bool] = None


class InteractionLogCreate(InteractionLogBase):
    """Schéma pour créer un log d'interaction."""
    pass


class InteractionLogUpdate(BaseModel):
    """Schéma pour mettre à jour un log."""
    charge_cognitive_estimee: Optional[float] = Field(None, ge=0.0, le=1.0)
    est_pertinent: Optional[bool] = None


class InteractionLogResponse(InteractionLogBase):
    """Schéma de réponse pour un log d'interaction."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Schéma enrichi avec contexte
class InteractionLogWithContext(InteractionLogResponse):
    """Schéma enrichi avec contexte de session."""
    learner_id: Optional[int] = None
    cas_clinique_id: Optional[int] = None
    session_statut: Optional[str] = None
    
    class Config:
        from_attributes = True


# Schéma pour batch creation
class InteractionLogBatchCreate(BaseModel):
    """Schéma pour créer plusieurs logs en batch."""
    session_id: UUID
    actions: list[Dict[str, Any]]