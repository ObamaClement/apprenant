"""Modèle SQLAlchemy pour les apprenants."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Learner(Base):
    """Apprenant du système STI."""
    __tablename__ = "learners"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String(50), unique=True, index=True, nullable=True)
    nom = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    niveau_etudes = Column(String(50), nullable=True)
    specialite_visee = Column(String(100), nullable=True)
    langue_preferee = Column(String(10), nullable=True)
    date_inscription = Column(DateTime(timezone=True), server_default=func.now())

    # Relations STI
    competency_masteries = relationship(
        "LearnerCompetencyMastery",
        back_populates="learner",
        foreign_keys="[LearnerCompetencyMastery.learner_id]"
    )
    
    simulation_sessions = relationship(
        "SimulationSession",
        back_populates="learner",
        foreign_keys="[SimulationSession.learner_id]"
    )
    
    behaviors = relationship(
        "LearnerBehavior",
        back_populates="learner",
        uselist=False
    )
    
    cognitive_profile = relationship(
        "LearnerCognitiveProfile",
        back_populates="learner",
        uselist=False
    )

    # Propriétés de compatibilité
    @property
    def first_name(self):
        return self.nom.split()[0] if self.nom else ""
    
    @property
    def last_name(self):
        parts = self.nom.split() if self.nom else []
        return " ".join(parts[1:]) if len(parts) > 1 else ""
    
    @property
    def level(self):
        return self.niveau_etudes
    
    @property
    def field_of_study(self):
        return self.specialite_visee
    
    @property
    def created_at(self):
        return self.date_inscription
    
    def __repr__(self):
        return f"<Learner(id={self.id}, matricule={self.matricule})>"