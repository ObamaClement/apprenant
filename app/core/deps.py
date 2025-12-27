"""Dépendances pour les routes FastAPI."""
from app.core.database import SessionLocal


def get_db():
    """Fournir une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
