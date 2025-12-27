"""Routes FastAPI pour les concepts pédagogiques."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.concept import Concept
from app.schemas.concept import ConceptCreate, ConceptResponse
from app.core.deps import get_db

router = APIRouter(prefix="/concepts", tags=["Concepts"])


@router.post("/", response_model=ConceptResponse)
def create_concept(concept: ConceptCreate, db: Session = Depends(get_db)):
    """Créer un nouveau concept pédagogique."""
    existing = db.query(Concept).filter(Concept.name == concept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Concept déjà existant")
    
    new_concept = Concept(**concept.dict())
    db.add(new_concept)
    db.commit()
    db.refresh(new_concept)
    return new_concept


@router.get("/", response_model=list[ConceptResponse])
def list_concepts(db: Session = Depends(get_db)):
    """Récupérer la liste de tous les concepts."""
    return db.query(Concept).all()


@router.get("/{concept_id}", response_model=ConceptResponse)
def get_concept(concept_id: int, db: Session = Depends(get_db)):
    """Récupérer un concept par ID."""
    concept = db.query(Concept).get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    return concept
