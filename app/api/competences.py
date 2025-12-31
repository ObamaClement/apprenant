### FICHIER 4: app/api/routes/competences.py
"""Routes FastAPI pour les compétences cliniques."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.deps import get_db
from app.models.competence_clinique import CompetenceClinique
from app.schemas.competence_clinique import (
    CompetenceCliniqueCreate,
    CompetenceCliniqueResponse,
    CompetenceCliniqueUpdate,
    CompetenceCliniqueWithPrerequisResponse
)
from app.services.competence_service import (
    get_all_competences,
    get_competence_by_id,
    get_competence_by_code,
    get_prerequis_for_competence,
    get_competences_depending_on,
    check_prerequisites_met,
    get_learning_path
)

router = APIRouter(prefix="/competences", tags=["Clinical Competencies"])


@router.post("/", response_model=CompetenceCliniqueResponse, status_code=201)
def create_competence(
    competence: CompetenceCliniqueCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle compétence clinique."""
    # Vérifier unicité du code
    existing = db.query(CompetenceClinique).filter(
        CompetenceClinique.code_competence == competence.code_competence
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Code compétence déjà existant")
    
    # Vérifier que le parent existe si fourni
    if competence.parent_competence_id:
        parent = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == competence.parent_competence_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Compétence parente non trouvée")
    
    new_comp = CompetenceClinique(**competence.model_dump())
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)
    return new_comp


@router.get("/", response_model=list[CompetenceCliniqueResponse])
def list_competences(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    categorie: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des compétences cliniques."""
    return get_all_competences(db, skip, limit, categorie)


@router.get("/{competence_id}", response_model=CompetenceCliniqueResponse)
def get_competence(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une compétence par ID."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    return comp


@router.get("/{competence_id}/with-prerequis", response_model=CompetenceCliniqueWithPrerequisResponse)
def get_competence_with_prerequis(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une compétence avec ses prérequis."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    prerequis = get_prerequis_for_competence(db, competence_id)
    prerequis_ids = [p.id for p in prerequis]
    
    comp_dict = {**comp.__dict__, "prerequis_ids": prerequis_ids}
    return comp_dict


@router.get("/code/{code_competence}", response_model=CompetenceCliniqueResponse)
def get_competence_by_code_endpoint(
    code_competence: str,
    db: Session = Depends(get_db)
):
    """Récupérer une compétence par code."""
    comp = get_competence_by_code(db, code_competence)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    return comp


@router.get("/categorie/{categorie}", response_model=list[CompetenceCliniqueResponse])
def get_competences_by_categorie(
    categorie: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les compétences d'une catégorie."""
    return get_all_competences(db, skip, limit, categorie)


@router.get("/{competence_id}/prerequis", response_model=list[CompetenceCliniqueResponse])
def get_prerequis(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les prérequis d'une compétence."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    return get_prerequis_for_competence(db, competence_id)


@router.get("/{competence_id}/depends", response_model=list[CompetenceCliniqueResponse])
def get_depends(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer les compétences qui dépendent de celle-ci."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    return get_competences_depending_on(db, competence_id)


@router.get("/{competence_id}/learning-path", response_model=list[CompetenceCliniqueResponse])
def get_learning_path_endpoint(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Construire un chemin d'apprentissage pour atteindre une compétence."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    return get_learning_path(db, competence_id)


@router.get("/check-prerequis/{learner_id}/{competence_id}")
def check_prerequis(
    learner_id: int,
    competence_id: int,
    threshold: float = Query(0.7, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Vérifier si un apprenant a les prérequis pour une compétence."""
    from app.models.learner import Learner
    
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    prerequis_met = check_prerequisites_met(db, competence_id, learner_id, threshold)
    prerequis = get_prerequis_for_competence(db, competence_id)
    
    return {
        "learner_id": learner_id,
        "competence_id": competence_id,
        "competence_code": comp.code_competence,
        "prerequis_met": prerequis_met,
        "threshold": threshold,
        "prerequis_count": len(prerequis),
        "message": "Prérequis satisfaits" if prerequis_met else "Prérequis non satisfaits"
    }


@router.put("/{competence_id}", response_model=CompetenceCliniqueResponse)
def update_competence(
    competence_id: int,
    competence_update: CompetenceCliniqueUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une compétence."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    update_dict = competence_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(comp, field, value)
    
    db.commit()
    db.refresh(comp)
    return comp


@router.delete("/{competence_id}", status_code=204)
def delete_competence(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une compétence."""
    comp = get_competence_by_id(db, competence_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    # Vérifier qu'elle n'a pas de compétences dépendantes
    dependents = get_competences_depending_on(db, competence_id)
    if dependents:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer: {len(dependents)} compétences en dépendent"
        )
    
    db.delete(comp)
    db.commit()
    return None


# ============================================================================
### FICHIER 5: app/api/routes/prerequis_competences.py

# ============================================================================
### FICHIER 6: app/api/routes/learner_competency_mastery.py
