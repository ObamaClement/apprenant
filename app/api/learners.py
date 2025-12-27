"""Routes FastAPI pour les apprenants."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.learner import Learner
from app.schemas.learner import LearnerCreate, LearnerResponse

router = APIRouter(prefix="/learners", tags=["Learners"])


@router.post("/", response_model=LearnerResponse)
def create_learner(learner: LearnerCreate, db: Session = Depends(get_db)):
    """Créer un nouvel apprenant."""
    existing = db.query(Learner).filter(Learner.email == learner.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_learner = Learner(**learner.dict())
    db.add(new_learner)
    db.commit()
    db.refresh(new_learner)
    return new_learner


@router.get("/", response_model=list[LearnerResponse])
def list_learners(db: Session = Depends(get_db)):
    """Récupérer la liste des apprenants."""
    return db.query(Learner).all()


@router.get("/{learner_id}", response_model=LearnerResponse)
def get_learner(learner_id: int, db: Session = Depends(get_db)):
    """Récupérer un apprenant par ID."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    return learner
