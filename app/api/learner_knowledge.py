"""Routes FastAPI pour le modèle de connaissances de l'apprenant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.learner_knowledge import LearnerKnowledge
from app.models.learner import Learner
from app.models.concept import Concept
from app.schemas.learner_knowledge import (
    LearnerKnowledgeCreate,
    LearnerKnowledgeResponse
)
from app.core.deps import get_db
from app.services.knowledge_update_service import get_mastery_label
from app.services.knowledge_inference_service import (
    get_learner_knowledge_summary,
    infer_knowledge_from_activity
)

router = APIRouter(
    prefix="/learner-knowledge",
    tags=["Learner Knowledge"]
)


@router.post("/", response_model=LearnerKnowledgeResponse)
def set_knowledge(
    data: LearnerKnowledgeCreate,
    db: Session = Depends(get_db)
):
    """Créer ou mettre à jour le niveau de maîtrise d'un concept pour un apprenant."""
    # Vérifier que l'apprenant existe
    learner = db.query(Learner).get(data.learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Vérifier que le concept existe
    concept = db.query(Concept).get(data.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    # Vérifier si l'enregistrement existe déjà
    existing = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == data.learner_id,
        LearnerKnowledge.concept_id == data.concept_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.mastery_level = data.mastery_level
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Créer
        lk = LearnerKnowledge(**data.dict())
        db.add(lk)
        db.commit()
        db.refresh(lk)
        return lk


@router.get("/learner/{learner_id}", response_model=list[LearnerKnowledgeResponse])
def get_learner_knowledge(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer le modèle de connaissances d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id
    ).all()


@router.get("/{learner_id}/{concept_id}", response_model=LearnerKnowledgeResponse)
def get_knowledge_for_concept(
    learner_id: int,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer le niveau de maîtrise d'un apprenant pour un concept spécifique."""
    lk = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id,
        LearnerKnowledge.concept_id == concept_id
    ).first()
    
    if not lk:
        raise HTTPException(status_code=404, detail="Enregistrement de connaissances non trouvé")
    
    return lk


@router.get("/summary/{learner_id}")
def get_knowledge_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un résumé des connaissances d'un apprenant."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    return get_learner_knowledge_summary(db, learner_id)


@router.post("/update-from-activity/{learner_id}/{concept_id}/{score}")
def update_knowledge_from_activity(
    learner_id: int,
    concept_id: int,
    score: float,
    db: Session = Depends(get_db)
):
    """Mettre à jour le niveau de maîtrise basé sur une activité."""
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    concept = db.query(Concept).get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    if not 0 <= score <= 100:
        raise HTTPException(status_code=400, detail="Le score doit être entre 0 et 100")
    
    lk = infer_knowledge_from_activity(db, learner_id, concept_id, score)
    
    return {
        "learner_id": learner_id,
        "concept_id": concept_id,
        "concept_name": concept.name,
        "score": score,
        "new_mastery_level": round(lk.mastery_level, 2),
        "message": "Niveau de maîtrise mis à jour"
    }


@router.delete("/{learner_id}/{concept_id}")
def delete_knowledge(
    learner_id: int,
    concept_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un enregistrement de connaissances."""
    lk = db.query(LearnerKnowledge).filter(
        LearnerKnowledge.learner_id == learner_id,
        LearnerKnowledge.concept_id == concept_id
    ).first()
    
    if not lk:
        raise HTTPException(status_code=404, detail="Enregistrement de connaissances non trouvé")
    
    db.delete(lk)
    db.commit()
    
    return {"message": "Enregistrement de connaissances supprimé avec succès"}
