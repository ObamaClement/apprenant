### FICHIER 11: app/api/routes/pathologies.py
"""Routes FastAPI pour les pathologies."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.deps import get_db
from app.models.pathologie import Pathologie
from app.schemas.pathologie import (
    PathologieCreate,
    PathologieResponse,
    PathologieUpdate,
    PathologieListResponse
)
from app.services.pathologie_service import (
    get_all_pathologies,
    get_pathologie_by_id,
    get_pathologie_by_icd10,
    search_pathologies,
    get_pathologies_by_gravite
)

router = APIRouter(prefix="/pathologies", tags=["Pathologies"])


@router.post("/", response_model=PathologieResponse, status_code=201)
def create_pathologie(
    pathologie: PathologieCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle pathologie."""
    # Vérifier unicité du code ICD10 si fourni
    if pathologie.code_icd10:
        existing = db.query(Pathologie).filter(
            Pathologie.code_icd10 == pathologie.code_icd10
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Code ICD10 déjà existant")
    
    new_path = Pathologie(**pathologie.model_dump())
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path


@router.get("/", response_model=list[PathologieListResponse])
def list_pathologies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    categorie: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des pathologies."""
    return get_all_pathologies(db, skip, limit, categorie)


@router.get("/{pathologie_id}", response_model=PathologieResponse)
def get_pathologie(
    pathologie_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une pathologie par ID."""
    path = get_pathologie_by_id(db, pathologie_id)
    if not path:
        raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    return path


@router.get("/icd10/{code_icd10}", response_model=PathologieResponse)
def get_pathologie_by_icd10_endpoint(
    code_icd10: str,
    db: Session = Depends(get_db)
):
    """Récupérer une pathologie par code ICD10."""
    path = get_pathologie_by_icd10(db, code_icd10)
    if not path:
        raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    return path


@router.get("/search/", response_model=list[PathologieListResponse])
def search_pathologies_endpoint(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Rechercher des pathologies par nom."""
    return search_pathologies(db, q, limit)


@router.get("/gravite/{niveau_min}", response_model=list[PathologieListResponse])
def get_by_gravite(
    niveau_min: int = Query(..., ge=1, le=5),
    niveau_max: int = Query(5, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """Récupérer les pathologies par niveau de gravité."""
    if niveau_min > niveau_max:
        raise HTTPException(
            status_code=400,
            detail="niveau_min doit être <= niveau_max"
        )
    
    return get_pathologies_by_gravite(db, niveau_min, niveau_max)


@router.get("/categorie/{categorie}", response_model=list[PathologieListResponse])
def get_by_categorie(
    categorie: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les pathologies d'une catégorie."""
    return get_all_pathologies(db, skip, limit, categorie)


@router.put("/{pathologie_id}", response_model=PathologieResponse)
def update_pathologie(
    pathologie_id: int,
    pathologie_update: PathologieUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une pathologie."""
    path = get_pathologie_by_id(db, pathologie_id)
    if not path:
        raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    
    update_dict = pathologie_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(path, field, value)
    
    db.commit()
    db.refresh(path)
    return path


@router.delete("/{pathologie_id}", status_code=204)
def delete_pathologie(
    pathologie_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une pathologie."""
    path = get_pathologie_by_id(db, pathologie_id)
    if not path:
        raise HTTPException(status_code=404, detail="Pathologie non trouvée")
    
    # Vérifier qu'elle n'est pas utilisée dans des cas cliniques
    from app.models.cas_clinique import CasCliniqueEnrichi
    used_in_cases = db.query(CasCliniqueEnrichi).filter(
        CasCliniqueEnrichi.pathologie_principale_id == pathologie_id
    ).count()
    
    if used_in_cases > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer: utilisée dans {used_in_cases} cas cliniques"
        )
    
    db.delete(path)
    db.commit()
    return None


# ============================================================================
### FICHIER 12: app/api/routes/symptomes.py



# ============================================================================
### FICHIER 13: app/api/routes/medicaments.py
