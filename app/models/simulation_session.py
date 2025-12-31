"""Modèle SQLAlchemy pour les sessions de simulation."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class SimulationSession(Base):
    """Session de simulation de cas clinique."""
    __tablename__ = "simulation_sessions"

    # Colonnes
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    cas_clinique_id = Column(Integer, ForeignKey("cas_cliniques_enrichis.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    score_final = Column(Float, nullable=True)
    temps_total = Column(Integer, nullable=True)
    cout_virtuel_genere = Column(Integer, nullable=True)
    statut = Column(String(50), nullable=True)
    raison_fin = Column(String(100), nullable=True)
    current_stage = Column(String(50), nullable=True)
    context_state = Column(JSON, nullable=True)

    # Relations STI
    learner = relationship(
        "Learner",
        back_populates="simulation_sessions",
        foreign_keys=[learner_id]
    )
    
    cas_clinique = relationship(
        "CasCliniqueEnrichi",
        back_populates="sessions",
        foreign_keys=[cas_clinique_id]
    )
    
    interaction_logs = relationship(
        "InteractionLog",
        back_populates="session",
        foreign_keys="[InteractionLog.session_id]"
    )
    
    affective_states = relationship(
        "LearnerAffectiveState",
        back_populates="session",
        foreign_keys="[LearnerAffectiveState.session_id]"
    )
    
    def __repr__(self):
        return f"<SimulationSession(id={self.id}, learner={self.learner_id}, status={self.statut})>"