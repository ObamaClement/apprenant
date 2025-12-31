"""Routes FastAPI pour les médicaments."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.deps import get_db
from app.models.medicament import Medicament
from app.schemas.medicament import (
    MedicamentCreate,
    MedicamentResponse,
    MedicamentUpdate,
    MedicamentListResponse
)

router = APIRouter(prefix="/medicaments", tags=["Medications"])


@router.post("/", response_model=MedicamentResponse, status_code=201)
def create_medicament(
    medicament: MedicamentCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouveau médicament."""
    # Vérifier unicité DCI
    existing = db.query(Medicament).filter(Medicament.dci == medicament.dci).first()
    if existing and existing.nom_commercial == medicament.nom_commercial:
        raise HTTPException(status_code=400, detail="Médicament déjà existant")
    
    new_med = Medicament(**medicament.model_dump())
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med


@router.get("/", response_model=list[MedicamentListResponse])
def list_medicaments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    classe_therapeutique: Optional[str] = None,
    disponibilite_cameroun: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des médicaments."""
    query = db.query(Medicament)
    
    if classe_therapeutique:
        query = query.filter(Medicament.classe_therapeutique == classe_therapeutique)
    
    if disponibilite_cameroun:
        query = query.filter(Medicament.disponibilite_cameroun == disponibilite_cameroun)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{medicament_id}", response_model=MedicamentResponse)
def get_medicament(
    medicament_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un médicament par ID."""
    med = db.query(Medicament).filter(Medicament.id == medicament_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    return med


@router.get("/dci/{dci}", response_model=list[MedicamentResponse])
def get_by_dci(
    dci: str,
    db: Session = Depends(get_db)
):
    """Récupérer les médicaments par DCI."""
    meds = db.query(Medicament).filter(Medicament.dci.ilike(f"%{dci}%")).all()
    if not meds:
        raise HTTPException(status_code=404, detail="Aucun médicament trouvé")
    return meds


@router.get("/search/", response_model=list[MedicamentListResponse])
def search_medicaments(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Rechercher des médicaments par nom commercial ou DCI."""
    search_pattern = f"%{q}%"
    meds = db.query(Medicament).filter(
        (Medicament.nom_commercial.ilike(search_pattern)) |
        (Medicament.dci.ilike(search_pattern))
    ).limit(limit).all()
    
    return meds


@router.get("/classe/{classe_therapeutique}", response_model=list[MedicamentListResponse])
def get_by_classe(
    classe_therapeutique: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les médicaments d'une classe thérapeutique."""
    return db.query(Medicament).filter(
        Medicament.classe_therapeutique == classe_therapeutique
    ).offset(skip).limit(limit).all()


@router.get("/disponibles/", response_model=list[MedicamentListResponse])
def get_disponibles_cameroun(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les médicaments disponibles au Cameroun."""
    return db.query(Medicament).filter(
        Medicament.disponibilite_cameroun.in_(["disponible", "largement_disponible"])
    ).offset(skip).limit(limit).all()


@router.get("/cout/", response_model=list[MedicamentListResponse])
def get_by_cout(
    cout_max: int = Query(..., ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupérer les médicaments par coût maximum."""
    return db.query(Medicament).filter(
        Medicament.cout_moyen_fcfa <= cout_max
    ).offset(skip).limit(limit).all()


@router.put("/{medicament_id}", response_model=MedicamentResponse)
def update_medicament(
    medicament_id: int,
    medicament_update: MedicamentUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un médicament."""
    med = db.query(Medicament).filter(Medicament.id == medicament_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    
    update_dict = medicament_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(med, field, value)
    
    db.commit()
    db.refresh(med)
    return med


@router.delete("/{medicament_id}", status_code=204)
def delete_medicament(
    medicament_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un médicament."""
    med = db.query(Medicament).filter(Medicament.id == medicament_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    
    db.delete(med)
    db.commit()
    return None


