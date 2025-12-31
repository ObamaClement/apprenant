"""Modèle SQLAlchemy pour la maîtrise des compétences."""
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerCompetencyMastery(Base):
    """Niveau de maîtrise d'une compétence par un apprenant."""
    __tablename__ = "learner_competency_mastery"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    competence_id = Column(Integer, ForeignKey("competences_cliniques.id"), nullable=False)
    mastery_level = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    last_practice_date = Column(DateTime(timezone=True), nullable=True)
    nb_success = Column(Integer, nullable=True)
    nb_failures = Column(Integer, nullable=True)
    streak_correct = Column(Integer, nullable=True)

    # Relations STI
    learner = relationship(
        "Learner",
        back_populates="competency_masteries",
        foreign_keys=[learner_id]
    )
    
    competence = relationship(
        "CompetenceClinique",
        back_populates="mastery_records",
        foreign_keys=[competence_id]
    )
    
    def __repr__(self):
        return f"<LearnerCompetencyMastery(learner={self.learner_id}, comp={self.competence_id}, mastery={self.mastery_level})>"