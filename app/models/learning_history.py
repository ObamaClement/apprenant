"""Modèle SQLAlchemy pour l'historique d'apprentissage."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningHistory(Base):
    """Historique des interactions apprenant–système."""
    __tablename__ = "learning_histories"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)

    activity_type = Column(String(50), nullable=False)
    activity_ref = Column(String(100), nullable=True)

    success = Column(Boolean, nullable=True)
    score = Column(Integer, nullable=True)
    time_spent = Column(Integer, nullable=True)  # en secondes

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learner = relationship("Learner", back_populates="learning_histories")
