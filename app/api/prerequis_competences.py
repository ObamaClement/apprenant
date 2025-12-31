
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.prerequis_competence import PrerequisCompetence
from app.models.competence_clinique import CompetenceClinique
from app.schemas.prerequis_competence import (
    PrerequisCompetenceCreate,
    PrerequisCompetenceResponse,
    PrerequisCompetenceUpdate,
    PrerequisCompetenceWithNames
)

router = APIRouter(prefix="/prerequis", tags=["Competency Prerequisites"])


@router.post("/", response_model=PrerequisCompetenceResponse, status_code=201)
def create_prerequis(
    prerequis: PrerequisCompetenceCreate,
    db: Session = Depends(get_db)
):
    """Créer une relation de prérequis."""
    # Vérifier que les deux compétences existent
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == prerequis.competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence cible non trouvée")
    
    prerequis_comp = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == prerequis.prerequis_id
    ).first()
    if not prerequis_comp:
        raise HTTPException(status_code=404, detail="Compétence prérequise non trouvée")
    
    # Éviter les cycles (une compétence ne peut être prérequis d'elle-même)
    if prerequis.competence_id == prerequis.prerequis_id:
        raise HTTPException(
            status_code=400,
            detail="Une compétence ne peut être prérequis d'elle-même"
        )
    
    # Vérifier que la relation n'existe pas déjà
    existing = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.competence_id == prerequis.competence_id,
        PrerequisCompetence.prerequis_id == prerequis.prerequis_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Relation de prérequis déjà existante")
    
    new_prerequis = PrerequisCompetence(**prerequis.model_dump())
    db.add(new_prerequis)
    db.commit()
    db.refresh(new_prerequis)
    return new_prerequis


@router.get("/competence/{competence_id}", response_model=list[PrerequisCompetenceWithNames])
def get_prerequis_for_competence(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer tous les prérequis d'une compétence."""
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    prerequis_relations = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.competence_id == competence_id
    ).all()
    
    # Enrichir avec les noms
    enriched = []
    for rel in prerequis_relations:
        comp = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == rel.competence_id
        ).first()
        prereq = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == rel.prerequis_id
        ).first()
        
        enriched.append({
            **rel.__dict__,
            "competence_code": comp.code_competence if comp else None,
            "competence_nom": comp.nom if comp else None,
            "prerequis_code": prereq.code_competence if prereq else None,
            "prerequis_nom": prereq.nom if prereq else None
        })
    
    return enriched


@router.get("/depends-on/{competence_id}", response_model=list[PrerequisCompetenceWithNames])
def get_depends_on_competence(
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les compétences qui dépendent de celle-ci."""
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    dependent_relations = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.prerequis_id == competence_id
    ).all()
    
    # Enrichir avec les noms
    enriched = []
    for rel in dependent_relations:
        comp = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == rel.competence_id
        ).first()
        prereq = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == rel.prerequis_id
        ).first()
        
        enriched.append({
            **rel.__dict__,
            "competence_code": comp.code_competence if comp else None,
            "competence_nom": comp.nom if comp else None,
            "prerequis_code": prereq.code_competence if prereq else None,
            "prerequis_nom": prereq.nom if prereq else None
        })
    
    return enriched


@router.put("/{prerequis_id}", response_model=PrerequisCompetenceResponse)
def update_prerequis(
    prerequis_id: int,
    prerequis_update: PrerequisCompetenceUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une relation de prérequis."""
    prerequis = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.id == prerequis_id
    ).first()
    if not prerequis:
        raise HTTPException(status_code=404, detail="Relation de prérequis non trouvée")
    
    update_dict = prerequis_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(prerequis, field, value)
    
    db.commit()
    db.refresh(prerequis)
    return prerequis


@router.delete("/{prerequis_id}", status_code=204)
def delete_prerequis(
    prerequis_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une relation de prérequis."""
    prerequis = db.query(PrerequisCompetence).filter(
        PrerequisCompetence.id == prerequis_id
    ).first()
    if not prerequis:
        raise HTTPException(status_code=404, detail="Relation de prérequis non trouvée")
    
    db.delete(prerequis)
    db.commit()
    return None

