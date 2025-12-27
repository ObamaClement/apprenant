"""Modèle SQLAlchemy pour les performances de l'apprenant."""
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerPerformance(Base):
    """Enregistre les performances d'un apprenant sur un concept."""
    __tablename__ = "learner_performances"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)

    activity_type = Column(String(50), nullable=False)  # quiz, exercice, test
    score = Column(Float, nullable=False)               # 0 - 100
    time_spent = Column(Integer, nullable=True)         # en secondes
    attempts = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learner = relationship("Learner")
    concept = relationship("Concept")
