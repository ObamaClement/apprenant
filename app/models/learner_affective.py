"""Modèle SQLAlchemy pour l'état affectif de l'apprenant."""
#État affectif courant de l’apprenant

from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerAffectiveState(Base):
    """Enregistre l'état affectif d'un apprenant."""
    __tablename__ = "learner_affective_states"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)

    motivation = Column(Float, default=0.5)      # 0.0 à 1.0
    frustration = Column(Float, default=0.0)     # 0.0 à 1.0
    confidence = Column(Float, default=0.5)      # 0.0 à 1.0
    stress = Column(Float, default=0.0)          # 0.0 à 1.0

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    learner = relationship("Learner")
