"""Routes FastAPI pour les apprenants."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.learner import Learner
from app.schemas.learner import LearnerCreate, LearnerResponse, LearnerUpdate

router = APIRouter(prefix="/learners", tags=["Learners"])


@router.post("/", response_model=LearnerResponse, status_code=201)
def create_learner(learner: LearnerCreate, db: Session = Depends(get_db)):
    """Créer un nouvel apprenant."""
    # Vérifier si l'email existe déjà
    existing_email = db.query(Learner).filter(Learner.email == learner.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Vérifier si le matricule existe déjà (si fourni)
    if learner.matricule:
        existing_matricule = db.query(Learner).filter(Learner.matricule == learner.matricule).first()
        if existing_matricule:
            raise HTTPException(status_code=400, detail="Matricule déjà utilisé")

    new_learner = Learner(**learner.model_dump())
    db.add(new_learner)
    db.commit()
    db.refresh(new_learner)
    return new_learner


@router.get("/", response_model=list[LearnerResponse])
def list_learners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des apprenants."""
    learners = db.query(Learner).offset(skip).limit(limit).all()
    return learners


@router.get("/{learner_id}", response_model=LearnerResponse)
def get_learner(learner_id: int, db: Session = Depends(get_db)):
    """Récupérer un apprenant par ID."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    return learner


@router.get("/matricule/{matricule}", response_model=LearnerResponse)
def get_learner_by_matricule(matricule: str, db: Session = Depends(get_db)):
    """Récupérer un apprenant par matricule."""
    learner = db.query(Learner).filter(Learner.matricule == matricule).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    return learner


@router.put("/{learner_id}", response_model=LearnerResponse)
def update_learner(
    learner_id: int,
    learner_update: LearnerUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Mettre à jour uniquement les champs fournis
    update_data = learner_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(learner, field, value)
    
    db.commit()
    db.refresh(learner)
    return learner


@router.delete("/{learner_id}", status_code=204)
def delete_learner(learner_id: int, db: Session = Depends(get_db)):
    """Supprimer un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    db.delete(learner)
    db.commit()
    return None