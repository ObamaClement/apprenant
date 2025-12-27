"""Schémas Pydantic pour les concepts pédagogiques."""
from pydantic import BaseModel, Field
from typing import Optional


class ConceptBase(BaseModel):
    """Schéma de base pour un concept."""
    name: str
    description: Optional[str] = None

    p_init: float = Field(default=0.2, ge=0.0, le=1.0)
    p_transit: float = Field(default=0.15, ge=0.0, le=1.0)
    p_guess: float = Field(default=0.2, ge=0.0, le=1.0)
    p_slip: float = Field(default=0.1, ge=0.0, le=1.0)


class ConceptCreate(ConceptBase):
    """Schéma pour créer un concept."""
    pass


class ConceptResponse(ConceptBase):
    """Schéma de réponse pour un concept."""
    id: int

    class Config:
        from_attributes = True
