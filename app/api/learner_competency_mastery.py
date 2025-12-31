"""Routes FastAPI pour la maîtrise des compétences (BKT)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.deps import get_db
from app.models.learner_competency_mastery import LearnerCompetencyMastery
from app.models.learner import Learner
from app.models.competence_clinique import CompetenceClinique
from app.schemas.learner_competency import (
    LearnerCompetencyMasteryCreate,
    LearnerCompetencyMasteryResponse,
    LearnerCompetencyMasteryUpdate,
    LearnerCompetencyMasteryWithCompetence
)
from app.services.knowledge_inference_service import (
    infer_knowledge_from_interaction,
    get_learner_knowledge_summary,
    identify_weak_competences
)
from app.services.knowledge_update_service import (
    get_mastery_label,
    calculate_confidence
)

router = APIRouter(prefix="/mastery", tags=["Competency Mastery"])


@router.post("/", response_model=LearnerCompetencyMasteryResponse, status_code=201)
def create_or_update_mastery(
    data: LearnerCompetencyMasteryCreate,
    db: Session = Depends(get_db)
):
    """Créer ou mettre à jour la maîtrise d'une compétence."""
    # Vérifications
    learner = db.query(Learner).filter(Learner.id == data.learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == data.competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    # Vérifier si existe déjà
    existing = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == data.learner_id,
        LearnerCompetencyMastery.competence_id == data.competence_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.mastery_level = data.mastery_level
        existing.confidence = data.confidence
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Créer
        mastery = LearnerCompetencyMastery(**data.model_dump())
        db.add(mastery)
        db.commit()
        db.refresh(mastery)
        return mastery


@router.get("/learner/{learner_id}", response_model=list[LearnerCompetencyMasteryWithCompetence])
def get_learner_masteries(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les maîtrises d'un apprenant."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    masteries = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id
    ).all()
    
    # Enrichir avec info de compétence
    enriched = []
    for m in masteries:
        comp = db.query(CompetenceClinique).filter(
            CompetenceClinique.id == m.competence_id
        ).first()
        
        enriched.append({
            **m.__dict__,
            "competence_code": comp.code_competence if comp else None,
            "competence_nom": comp.nom if comp else None,
            "competence_categorie": comp.categorie if comp else None
        })
    
    return enriched


@router.get("/{learner_id}/{competence_id}", response_model=LearnerCompetencyMasteryResponse)
def get_mastery(
    learner_id: int,
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer la maîtrise d'une compétence spécifique."""
    mastery = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id,
        LearnerCompetencyMastery.competence_id == competence_id
    ).first()
    
    if not mastery:
        raise HTTPException(status_code=404, detail="Maîtrise non trouvée")
    
    return mastery


@router.get("/summary/{learner_id}")
def get_knowledge_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un résumé complet des connaissances."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_learner_knowledge_summary(db, learner_id)


@router.get("/weak/{learner_id}")
def get_weak_competences(
    learner_id: int,
    threshold: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Identifier les compétences faibles."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    weak_comps = identify_weak_competences(db, learner_id, threshold)
    
    return {
        "learner_id": learner_id,
        "threshold": threshold,
        "weak_competences_count": len(weak_comps),
        "weak_competences": weak_comps
    }


@router.post("/update-from-score")
def update_from_score(
    learner_id: int = Query(...),
    competence_id: int = Query(...),
    score: float = Query(..., ge=0.0, le=100.0),
    correct: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Mettre à jour la maîtrise basée sur un score (BKT)."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    competence = db.query(CompetenceClinique).filter(
        CompetenceClinique.id == competence_id
    ).first()
    if not competence:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    
    mastery = infer_knowledge_from_interaction(db, learner_id, competence_id, score, correct)
    
    return {
        "learner_id": learner_id,
        "competence_id": competence_id,
        "competence_code": competence.code_competence,
        "score": score,
        "new_mastery_level": round(mastery.mastery_level or 0, 2),
        "confidence": round(mastery.confidence or 0, 2),
        "mastery_label": get_mastery_label(mastery.mastery_level or 0),
        "message": "Maîtrise mise à jour via BKT"
    }


@router.put("/{learner_id}/{competence_id}", response_model=LearnerCompetencyMasteryResponse)
def update_mastery(
    learner_id: int,
    competence_id: int,
    mastery_update: LearnerCompetencyMasteryUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une maîtrise."""
    mastery = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id,
        LearnerCompetencyMastery.competence_id == competence_id
    ).first()
    
    if not mastery:
        raise HTTPException(status_code=404, detail="Maîtrise non trouvée")
    
    update_dict = mastery_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(mastery, field, value)
    
    db.commit()
    db.refresh(mastery)
    return mastery


@router.delete("/{learner_id}/{competence_id}", status_code=204)
def delete_mastery(
    learner_id: int,
    competence_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un enregistrement de maîtrise."""
    mastery = db.query(LearnerCompetencyMastery).filter(
        LearnerCompetencyMastery.learner_id == learner_id,
        LearnerCompetencyMastery.competence_id == competence_id
    ).first()
    
    if not mastery:
        raise HTTPException(status_code=404, detail="Maîtrise non trouvée")
    
    db.delete(mastery)
    db.commit()
    return None