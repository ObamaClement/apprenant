"""Modèle SQLAlchemy pour le modèle de connaissances de l'apprenant."""
#Lien entre apprenant et connaissances
# implémente l’overlay model

from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerKnowledge(Base):
    """Représente le niveau de maîtrise d'un apprenant sur un concept."""
    __tablename__ = "learner_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)

    mastery_level = Column(Float, default=0.0)  # entre 0 et 1

    learner = relationship("Learner", back_populates="knowledge")
    concept = relationship("Concept")
