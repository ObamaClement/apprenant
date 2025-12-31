"""Modèle SQLAlchemy pour le profil cognitif."""
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerCognitiveProfile(Base):
    """Profil cognitif d'un apprenant."""
    __tablename__ = "learner_cognitive_profiles"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), unique=True, nullable=True)
    vitesse_assimilation = Column(Float, nullable=True)
    capacite_memoire_travail = Column(Float, nullable=True)
    tendance_impulsivite = Column(Float, nullable=True)
    prefer_visual = Column(Boolean, nullable=True)

    # Relations STI
    learner = relationship(
        "Learner",
        back_populates="cognitive_profile",
        foreign_keys=[learner_id]
    )
    
    # Propriétés compatibilité
    @property
    def learning_style(self):
        if self.prefer_visual is True:
            return "visuel"
        elif self.prefer_visual is False:
            return "auditif"
        return None
    
    @property
    def learning_speed(self):
        return self.vitesse_assimilation
    
    @property
    def autonomy_level(self):
        if self.tendance_impulsivite is not None:
            return 1.0 - self.tendance_impulsivite
        return None
    
    def __repr__(self):
        return f"<LearnerCognitiveProfile(learner={self.learner_id})>"