"""Modèle SQLAlchemy pour les concepts pédagogiques."""
#Définit les concepts / compétences du domaine enseigné.
# C'est la Base du modèle cognitif et un Support pour l’overlay model

from sqlalchemy import Column, Integer, String, Text, Float
from app.core.database import Base


class Concept(Base):
    """Représente un concept pédagogique (notion à enseigner)."""
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    p_init = Column(Float, nullable=False, default=0.2)
    p_transit = Column(Float, nullable=False, default=0.15)
    p_guess = Column(Float, nullable=False, default=0.2)
    p_slip = Column(Float, nullable=False, default=0.1)
