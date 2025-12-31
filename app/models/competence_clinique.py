"""Modèle SQLAlchemy pour les compétences cliniques."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CompetenceClinique(Base):
    """Compétence clinique à acquérir."""
    __tablename__ = "competences_cliniques"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    code_competence = Column(String(50), unique=True, index=True, nullable=False)
    nom = Column(String(255), nullable=False)
    categorie = Column(String(100), index=True, nullable=True)
    niveau_bloom = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    objectifs_apprentissage = Column(JSON, nullable=True)
    criteres_maitrise = Column(JSON, nullable=True)
    parent_competence_id = Column(Integer, nullable=True)
    ordre_apprentissage = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations STI
    mastery_records = relationship(
        "LearnerCompetencyMastery",
        back_populates="competence",
        foreign_keys="[LearnerCompetencyMastery.competence_id]"
    )
    
    prerequis_as_competence = relationship(
        "PrerequisCompetence",
        foreign_keys="[PrerequisCompetence.competence_id]",
        back_populates="competence"
    )
    
    prerequis_as_prerequis = relationship(
        "PrerequisCompetence",
        foreign_keys="[PrerequisCompetence.prerequis_id]",
        back_populates="prerequis"
    )

    # Propriétés compatibilité BKT
    @property
    def name(self):
        return self.code_competence
    
    @property
    def p_init(self):
        return 0.2
    
    @property
    def p_transit(self):
        return 0.15
    
    @property
    def p_guess(self):
        return 0.2
    
    @property
    def p_slip(self):
        return 0.1
    
    def __repr__(self):
        return f"<CompetenceClinique(id={self.id}, code={self.code_competence})>"