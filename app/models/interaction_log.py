"""Modèle SQLAlchemy pour les logs d'interaction."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class InteractionLog(Base):
    """Action détaillée de l'apprenant dans une session."""
    __tablename__ = "interaction_logs"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("simulation_sessions.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_category = Column(String(50), nullable=True)
    action_type = Column(String(100), nullable=True)
    action_content = Column(JSON, nullable=True)
    response_latency = Column(Integer, nullable=True)
    charge_cognitive_estimee = Column(Float, nullable=True)
    est_pertinent = Column(Boolean, nullable=True)

    # Relations STI
    session = relationship(
        "SimulationSession",
        back_populates="interaction_logs",
        foreign_keys=[session_id]
    )
    
    def __repr__(self):
        return f"<InteractionLog(id={self.id}, session={self.session_id}, action={self.action_type})>"