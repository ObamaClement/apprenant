"""Schémas Pydantic pour les sessions de simulation."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SimulationSessionBase(BaseModel):
    """Schéma de base pour une session de simulation."""
    learner_id: int
    cas_clinique_id: int
    statut: Optional[str] = "en_cours"
    current_stage: Optional[str] = None


class SimulationSessionCreate(SimulationSessionBase):
    """Schéma pour créer une session de simulation."""
    pass


class SimulationSessionUpdate(BaseModel):
    """Schéma pour mettre à jour une session."""
    score_final: Optional[float] = Field(None, ge=0.0, le=100.0)
    temps_total: Optional[int] = Field(None, ge=0)
    cout_virtuel_genere: Optional[int] = None
    statut: Optional[str] = None
    raison_fin: Optional[str] = None
    current_stage: Optional[str] = None
    context_state: Optional[Dict[str, Any]] = None


class SimulationSessionComplete(BaseModel):
    """Schéma pour terminer une session."""
    score_final: float = Field(ge=0.0, le=100.0)
    raison_fin: str
    context_state: Optional[Dict[str, Any]] = None


class SimulationSessionResponse(SimulationSessionBase):
    """Schéma de réponse pour une session."""
    id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    score_final: Optional[float] = None
    temps_total: Optional[int] = None
    cout_virtuel_genere: Optional[int] = None
    raison_fin: Optional[str] = None
    context_state: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Schéma enrichi avec détails
class SimulationSessionWithDetails(SimulationSessionResponse):
    """Schéma enrichi avec les détails du cas et de l'apprenant."""
    learner_nom: Optional[str] = None
    learner_matricule: Optional[str] = None
    cas_code_fultang: Optional[str] = None
    cas_niveau_difficulte: Optional[int] = None
    nb_interactions: Optional[int] = None
    
    class Config:
        from_attributes = True