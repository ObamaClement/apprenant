"""Modèle SQLAlchemy pour les prérequis entre compétences."""
from sqlalchemy import Column, Integer, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class PrerequisCompetence(Base):
    """Relation de prérequis entre deux compétences."""
    __tablename__ = "prerequis_competences"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    competence_id = Column(Integer, ForeignKey("competences_cliniques.id"), nullable=False)
    prerequis_id = Column(Integer, ForeignKey("competences_cliniques.id"), nullable=False)
    type_relation = Column(String(50), nullable=True)
    force_relation = Column(Numeric(3, 2), nullable=True)

    # Relations STI
    competence = relationship(
        "CompetenceClinique",
        foreign_keys=[competence_id],
        back_populates="prerequis_as_competence"
    )
    
    prerequis = relationship(
        "CompetenceClinique",
        foreign_keys=[prerequis_id],
        back_populates="prerequis_as_prerequis"
    )
    
    def __repr__(self):
        return f"<PrerequisCompetence(comp={self.competence_id}, prereq={self.prerequis_id})>"