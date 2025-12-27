"""Modèle SQLAlchemy pour le comportement de l'apprenant."""
#Modélise le comportement d’apprentissage

from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerBehavior(Base):
    """Enregistre les indicateurs comportementaux d'un apprenant."""
    __tablename__ = "learner_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)

    sessions_count = Column(Integer, default=0)
    activities_count = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # en secondes

    engagement_score = Column(Float, default=0.0)  # 0 à 1

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    learner = relationship("Learner")
