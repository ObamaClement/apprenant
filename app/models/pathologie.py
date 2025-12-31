"""Modèle SQLAlchemy pour les pathologies."""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Pathologie(Base):
    """Pathologie médicale."""
    __tablename__ = "pathologies"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    code_icd10 = Column(String(20), unique=True, index=True, nullable=True)
    nom_fr = Column(String(255), index=True, nullable=False)
    nom_en = Column(String(255), nullable=True)
    nom_local = Column(String(255), nullable=True)
    categorie = Column(String(100), index=True, nullable=True)
    prevalence_cameroun = Column(Numeric(5, 2), nullable=True)
    niveau_gravite = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    physiopathologie = Column(Text, nullable=True)
    evolution_naturelle = Column(Text, nullable=True)
    complications = Column(JSON, nullable=True)
    facteurs_risque = Column(JSON, nullable=True)
    prevention = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Pathologie(id={self.id}, icd10={self.code_icd10}, nom={self.nom_fr})>"