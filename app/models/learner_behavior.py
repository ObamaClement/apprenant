"""Modèle SQLAlchemy pour le comportement de l'apprenant."""
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerBehavior(Base):
    """Enregistre les indicateurs comportementaux d'un apprenant."""
    __tablename__ = "learner_behaviors"

    # Colonnes (100% conformes à la base STI)
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    sessions_count = Column(Integer, nullable=True)
    activities_count = Column(Integer, nullable=True)
    total_time_spent = Column(Integer, nullable=True)
    engagement_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations (100% conformes à la base STI)
    learner = relationship("Learner", back_populates="behaviors")
    
    def __repr__(self):
        return f"<LearnerBehavior(learner_id={self.learner_id}, engagement={self.engagement_score})>""""Modèle SQLAlchemy pour le comportement."""
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerBehavior(Base):
    """Indicateurs comportementaux d'un apprenant."""
    __tablename__ = "learner_behaviors"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    sessions_count = Column(Integer, nullable=True)
    activities_count = Column(Integer, nullable=True)
    total_time_spent = Column(Integer, nullable=True)
    engagement_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations STI
    learner = relationship(
        "Learner",
        back_populates="behaviors",
        foreign_keys=[learner_id]
    )
    
    def __repr__(self):
        return f"<LearnerBehavior(learner={self.learner_id}, engagement={self.engagement_score})>"