"""Modèle SQLAlchemy pour le profil cognitif de l'apprenant."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerCognitiveProfile(Base):
    """Enregistre le profil cognitif d'un apprenant."""
    __tablename__ = "learner_cognitive_profiles"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)

    learning_style = Column(String(50), nullable=True)  # visuel, auditif, kinesthésique
    learning_speed = Column(Float, nullable=True)       # 0 à 1 (lent à rapide)
    autonomy_level = Column(Float, nullable=True)       # 0 à 1 (dépendant à autonome)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    learner = relationship("Learner")
