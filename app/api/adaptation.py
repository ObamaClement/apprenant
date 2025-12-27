"""Routes FastAPI pour le moteur d'adaptation intelligente."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.learner import Learner
from app.models.concept import Concept
from app.services.adaptation_engine import (
    process_new_performance,
    get_adaptation_summary
)

router = APIRouter(prefix="/adaptation", tags=["Adaptation Engine"])


@router.post("/process")
def process_adaptation(
    learner_id: int,
    concept_id: int,
    score: float = Query(ge=0.0, le=100.0),
    activity_type: str = "exercice",
    time_spent: int = None,
    db: Session = Depends(get_db)
):
    """
    Orchestration complète après une nouvelle performance.
    
    Flux:
    1. Enregistrer la performance
    2. Mettre à jour le niveau de maîtrise
    3. Mettre à jour l'état affectif
    4. Générer une recommandation pédagogique
    
    Args:
        learner_id: ID de l'apprenant
        concept_id: ID du concept
        score: Score obtenu (0-100)
        activity_type: Type d'activité (quiz, exercice, test)
        time_spent: Temps passé en secondes
    
    Returns:
        Résultats complets de l'adaptation
    """
    # Vérifier que l'apprenant existe
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Vérifier que le concept existe
    concept = db.query(Concept).get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept non trouvé")
    
    # Valider le score
    if not 0 <= score <= 100:
        raise HTTPException(status_code=400, detail="Le score doit être entre 0 et 100")
    
    # Valider le type d'activité
    valid_types = ["quiz", "exercice", "test", "projet", "devoir"]
    if activity_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type d'activité invalide. Doit être l'un de: {', '.join(valid_types)}"
        )
    
    # Traiter la performance et générer l'adaptation
    result = process_new_performance(
        db,
        learner_id,
        concept_id,
        score,
        activity_type,
        time_spent
    )
    
    return result


@router.get("/summary/{learner_id}")
def get_adaptation_summary_endpoint(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtenir un résumé complet de l'adaptation pour un apprenant.
    
    Inclut:
    - Modèle de connaissances
    - Modèle de performances
    - Modèle affectif
    - Modèle comportemental
    - Statut global
    
    Args:
        learner_id: ID de l'apprenant
    
    Returns:
        Résumé complet de l'adaptation
    """
    # Vérifier que l'apprenant existe
    learner = db.query(Learner).get(learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    summary = get_adaptation_summary(db, learner_id)
    
    return summary


@router.post("/batch-process")
def batch_process_adaptations(
    data: list[dict],
    db: Session = Depends(get_db)
):
    """
    Traiter plusieurs performances en batch.
    
    Args:
        data: Liste de dictionnaires avec learner_id, concept_id, score
    
    Returns:
        Résultats pour chaque performance
    """
    results = []
    
    for item in data:
        try:
            learner_id = item.get("learner_id")
            concept_id = item.get("concept_id")
            score = item.get("score")
            activity_type = item.get("activity_type", "exercice")
            time_spent = item.get("time_spent")
            
            # Vérifications basiques
            if not all([learner_id, concept_id, score is not None]):
                results.append({
                    "status": "error",
                    "message": "Données manquantes (learner_id, concept_id, score)"
                })
                continue
            
            if not 0 <= score <= 100:
                results.append({
                    "status": "error",
                    "learner_id": learner_id,
                    "message": "Score invalide"
                })
                continue
            
            # Traiter la performance
            result = process_new_performance(
                db,
                learner_id,
                concept_id,
                score,
                activity_type,
                time_spent
            )
            
            results.append({
                "status": "success",
                "learner_id": learner_id,
                "concept_id": concept_id,
                "score": score,
                "recommendation": result["recommendation"]
            })
        
        except Exception as e:
            results.append({
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total": len(data),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"]),
        "results": results
    }


@router.get("/health")
def adaptation_engine_health(db: Session = Depends(get_db)):
    """Vérifier la santé du moteur d'adaptation."""
    try:
        # Tester la connexion à la base de données
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "engine": "Adaptation Engine",
            "version": "1.0.0",
            "message": "Moteur d'adaptation opérationnel"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Moteur d'adaptation indisponible: {str(e)}"
        )
