"""Modèle SQLAlchemy pour les cas cliniques."""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.core.database import Base


class CasCliniqueEnrichi(Base):
    """Cas clinique complet pour simulation."""
    __tablename__ = "cas_cliniques_enrichis"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    code_fultang = Column(String(100), unique=True, index=True, nullable=True)
    hash_integrite = Column(String(64), nullable=True)
    pathologie_principale_id = Column(Integer, ForeignKey("pathologies.id"), index=True, nullable=True)
    donnees_brutes = Column(JSON, nullable=True)
    presentation_clinique = Column(JSON, nullable=False)
    donnees_paracliniques = Column(JSON, nullable=True)
    evolution_patient = Column(Text, nullable=True)
    images_associees_ids = Column(ARRAY(Integer), nullable=True)
    sons_associes_ids = Column(ARRAY(Integer), nullable=True)
    medicaments_prescrits = Column(JSON, nullable=True)
    niveau_difficulte = Column(Integer, nullable=True)
    duree_estimee_resolution_min = Column(Integer, nullable=True)
    objectifs_apprentissage = Column(JSON, nullable=True)
    competences_requises = Column(JSON, nullable=True)
    valide_expert = Column(Boolean, nullable=True)
    date_validation = Column(Date, nullable=True)
    qualite_donnees = Column(Integer, nullable=True)
    nb_utilisations = Column(Integer, nullable=True)
    note_moyenne_apprenants = Column(Numeric(3, 2), nullable=True)
    taux_succes_diagnostic = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    pathologies_secondaires_ids = Column(ARRAY(Integer), nullable=True)
    expert_validateur_id = Column(Integer, nullable=True)

    # Relations STI
    pathologie_principale = relationship(
        "Pathologie",
        foreign_keys=[pathologie_principale_id]
    )
    
    sessions = relationship(
        "SimulationSession",
        back_populates="cas_clinique",
        foreign_keys="[SimulationSession.cas_clinique_id]"
    )
    
    def __repr__(self):
        return f"<CasCliniqueEnrichi(id={self.id}, code={self.code_fultang})>"