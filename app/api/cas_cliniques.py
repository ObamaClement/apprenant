from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.deps import get_db
from app.models.cas_clinique import CasCliniqueEnrichi
from app.models.pathologie import Pathologie
from app.schemas.cas_clinique import (
    CasCliniqueCreate,
    CasCliniqueResponse,
    CasCliniqueUpdate,
    CasCliniqueListResponse
)
from app.services.cas_clinique_service import (
    get_all_cases,
    get_case_by_id,
    get_case_by_code,
    get_cases_by_pathologie,
    get_cases_by_competences,
    increment_case_usage,
    update_case_statistics,
    get_recommended_cases_for_learner
)

router = APIRouter(prefix="/cases", tags=["Clinical Cases"])


@router.post("/", response_model=CasCliniqueResponse, status_code=201)
def create_case(
    case: CasCliniqueCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouveau cas clinique."""
    # Vérifier que la pathologie existe si fournie
    if case.pathologie_principale_id:
        pathologie = db.query(Pathologie).filter(
            Pathologie.id == case.pathologie_principale_id
        ).first()
        if not pathologie:
            raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    
    # Vérifier unicité du code Fultang
    if case.code_fultang:
        existing = db.query(CasCliniqueEnrichi).filter(
            CasCliniqueEnrichi.code_fultang == case.code_fultang
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Code Fultang déjà existant")
    
    new_case = CasCliniqueEnrichi(**case.model_dump())
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case


@router.get("/", response_model=list[CasCliniqueListResponse])
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    niveau_difficulte: Optional[int] = Query(None, ge=1, le=5),
    valide_expert: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des cas cliniques."""
    return get_all_cases(db, skip, limit, niveau_difficulte, valide_expert)


@router.get("/{cas_id}", response_model=CasCliniqueResponse)
def get_case(
    cas_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un cas clinique par ID."""
    case = get_case_by_id(db, cas_id)
    if not case:
        raise HTTPException(status_code=404, detail="Cas clinique non trouvé")
    return case


@router.get("/code/{code_fultang}", response_model=CasCliniqueResponse)
def get_case_by_code_endpoint(
    code_fultang: str,
    db: Session = Depends(get_db)
):
    """Récupérer un cas clinique par code Fultang."""
    case = get_case_by_code(db, code_fultang)
    if not case:
        raise HTTPException(status_code=404, detail="Cas clinique non trouvé")
    return case


@router.get("/pathologie/{pathologie_id}", response_model=list[CasCliniqueListResponse])
def get_cases_by_pathologie_endpoint(
    pathologie_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les cas pour une pathologie donnée."""
    pathologie = db.query(Pathologie).filter(Pathologie.id == pathologie_id).first()
    if not pathologie:
        raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    
    return get_cases_by_pathologie(db, pathologie_id, skip, limit)


@router.post("/by-competences", response_model=list[CasCliniqueListResponse])
def get_cases_by_competences_endpoint(
    competences_ids: List[int],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les cas qui sollicitent des compétences données."""
    if not competences_ids:
        raise HTTPException(status_code=400, detail="Liste de compétences vide")
    
    return get_cases_by_competences(db, competences_ids, skip, limit)


@router.get("/recommend/{learner_id}")
def recommend_cases(
    learner_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Recommander des cas adaptés au niveau de l'apprenant."""
    from app.models.learner import Learner
    
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    recommendations = get_recommended_cases_for_learner(db, learner_id, limit)
    
    return {
        "learner_id": learner_id,
        "recommendations": [
            {
                "case_id": rec["case"].id,
                "code_fultang": rec["case"].code_fultang,
                "niveau_difficulte": rec["case"].niveau_difficulte,
                "relevance_score": rec["relevance_score"],
                "reason": rec["reason"]
            }
            for rec in recommendations
        ]
    }


@router.post("/{cas_id}/increment-usage")
def increment_usage(
    cas_id: int,
    db: Session = Depends(get_db)
):
    """Incrémenter le compteur d'utilisation d'un cas."""
    case = get_case_by_id(db, cas_id)
    if not case:
        raise HTTPException(status_code=404, detail="Cas clinique non trouvé")
    
    increment_case_usage(db, cas_id)
    
    return {
        "cas_id": cas_id,
        "message": "Compteur d'utilisation incrémenté",
        "nb_utilisations": (case.nb_utilisations or 0) + 1
    }


@router.put("/{cas_id}", response_model=CasCliniqueResponse)
def update_case(
    cas_id: int,
    case_update: CasCliniqueUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un cas clinique."""
    case = get_case_by_id(db, cas_id)
    if not case:
        raise HTTPException(status_code=404, detail="Cas clinique non trouvé")
    
    update_dict = case_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{cas_id}", status_code=204)
def delete_case(
    cas_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un cas clinique."""
    case = get_case_by_id(db, cas_id)
    if not case:
        raise HTTPException(status_code=404, detail="Cas clinique non trouvé")
    
    db.delete(case)
    db.commit()
    return None