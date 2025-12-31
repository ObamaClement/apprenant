"""Modèle SQLAlchemy pour l'état affectif."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class LearnerAffectiveState(Base):
    """État affectif d'un apprenant lors d'une session."""
    __tablename__ = "learner_affective_states"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("simulation_sessions.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    stress_level = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    motivation_level = Column(Float, nullable=True)
    frustration_level = Column(Float, nullable=True)

    # Relations STI
    session = relationship(
        "SimulationSession",
        back_populates="affective_states",
        foreign_keys=[session_id]
    )
    
    # Propriétés compatibilité
    @property
    def learner_id(self):
        return self.session.learner_id if self.session else None
    
    @property
    def stress(self):
        return self.stress_level
    
    @property
    def confidence(self):
        return self.confidence_level
    
    @property
    def motivation(self):
        return self.motivation_level
    
    @property
    def frustration(self):
        return self.frustration_level
    
    def __repr__(self):
        return f"<LearnerAffectiveState(session={self.session_id}, motivation={self.motivation_level})>"