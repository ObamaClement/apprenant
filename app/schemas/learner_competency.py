"""Schémas Pydantic pour la maîtrise des compétences."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LearnerCompetencyMasteryBase(BaseModel):
    """Schéma de base pour la maîtrise d'une compétence."""
    learner_id: int
    competence_id: int
    mastery_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class LearnerCompetencyMasteryCreate(LearnerCompetencyMasteryBase):
    """Schéma pour créer un enregistrement de maîtrise."""
    pass


class LearnerCompetencyMasteryUpdate(BaseModel):
    """Schéma pour mettre à jour la maîtrise."""
    mastery_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    nb_success: Optional[int] = None
    nb_failures: Optional[int] = None
    streak_correct: Optional[int] = None


class LearnerCompetencyMasteryResponse(LearnerCompetencyMasteryBase):
    """Schéma de réponse pour la maîtrise."""
    id: int
    last_practice_date: Optional[datetime] = None
    nb_success: Optional[int] = None
    nb_failures: Optional[int] = None
    streak_correct: Optional[int] = None

    class Config:
        from_attributes = True


# Schéma enrichi avec info de compétence
class LearnerCompetencyMasteryWithCompetence(LearnerCompetencyMasteryResponse):
    """Schéma enrichi avec les détails de la compétence."""
    competence_code: Optional[str] = None
    competence_nom: Optional[str] = None
    competence_categorie: Optional[str] = None

    class Config:
        from_attributes = True