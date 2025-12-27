"""Schémas Pydantic pour le modèle de connaissances de l'apprenant."""
from pydantic import BaseModel, Field


class LearnerKnowledgeBase(BaseModel):
    """Schéma de base pour le modèle de connaissances."""
    learner_id: int
    concept_id: int
    mastery_level: float = Field(ge=0.0, le=1.0)


class LearnerKnowledgeCreate(LearnerKnowledgeBase):
    """Schéma pour créer un enregistrement de connaissances."""
    pass


class LearnerKnowledgeResponse(LearnerKnowledgeBase):
    """Schéma de réponse pour le modèle de connaissances."""
    id: int

    class Config:
        from_attributes = True
