"""Modèle SQLAlchemy pour les médicaments."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Medicament(Base):
    """Médicament."""
    __tablename__ = "medicaments"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    nom_commercial = Column(String(255), index=True, nullable=True)
    dci = Column(String(255), index=True, nullable=False)
    classe_therapeutique = Column(String(255), index=True, nullable=True)
    forme_galenique = Column(String(100), nullable=True)
    dosage = Column(String(100), nullable=True)
    voie_administration = Column(String(100), nullable=True)
    mecanisme_action = Column(Text, nullable=True)
    indications = Column(JSON, nullable=True)
    contre_indications = Column(JSON, nullable=True)
    effets_secondaires = Column(JSON, nullable=True)
    interactions_medicamenteuses = Column(JSON, nullable=True)
    precautions_emploi = Column(Text, nullable=True)
    posologie_standard = Column(JSON, nullable=True)
    disponibilite_cameroun = Column(String(50), nullable=True)
    cout_moyen_fcfa = Column(Integer, nullable=True)
    statut_prescription = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Medicament(id={self.id}, dci={self.dci})>"