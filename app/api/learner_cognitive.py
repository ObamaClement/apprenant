"""Modèle SQLAlchemy pour le profil cognitif de l'apprenant."""
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerCognitiveProfile(Base):
    """Enregistre le profil cognitif d'un apprenant - Compatible STI."""
    __tablename__ = "learner_cognitive_profiles"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), unique=True, nullable=True)

    # Colonnes de la base STI (conformes au schéma déployé)
    vitesse_assimilation = Column(Float, nullable=True)
    capacite_memoire_travail = Column(Float, nullable=True)
    tendance_impulsivite = Column(Float, nullable=True)
    prefer_visual = Column(Boolean, nullable=True)

    # Relation
    learner = relationship("Learner", back_populates="cognitive_profile")
    
    # Propriétés de compatibilité pour l'ancien code
    @property
    def learning_style(self):
        """Compatibilité : déduit le style d'apprentissage"""
        if self.prefer_visual:
            return "visuel"
        return "auditif"
    
    @property
    def learning_speed(self):
        """Compatibilité : alias pour vitesse_assimilation"""
        return self.vitesse_assimilation
    
    @property
    def autonomy_level(self):
        """Compatibilité : calculé depuis tendance_impulsivite"""
        if self.tendance_impulsivite is not None:
            return 1.0 - self.tendance_impulsivite  # Autonomie inverse de l'impulsivité
        return None
    
    def __repr__(self):
        return f"<LearnerCognitiveProfile(id={self.id}, learner_id={self.learner_id})>"