"""Modèle SQLAlchemy pour les symptômes."""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Symptome(Base):
    """Symptôme médical."""
    __tablename__ = "symptomes"

    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), unique=True, index=True, nullable=False)
    nom_local = Column(String(255), nullable=True)
    categorie = Column(String(100), index=True, nullable=True)
    type_symptome = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    questions_anamnese = Column(JSON, nullable=True)
    signes_alarme = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Symptome(id={self.id}, nom={self.nom})>"