### FICHIER 7: app/api/routes/adaptation_engine.py
"""Routes FastAPI pour le moteur d'adaptation intelligente - CRITIQUE."""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from app.core.deps import get_db
from app.models.learner import Learner
from app.models.simulation_session import SimulationSession
from app.services.adaptation_engine import (
    process_simulation_completion,
    get_adaptation_summary
)

router = APIRouter(prefix="/adaptation", tags=["Adaptation Engine"])


@router.post("/process-simulation")
def process_simulation(
    session_id: UUID = Body(...),
    actions: List[Dict[str, Any]] = Body(...),
    diagnostic_propose: str = Body(...),
    diagnostic_correct: bool = Body(...),
    db: Session = Depends(get_db)
):
    """
    Traiter la fin d'une simulation complète (orchestration).
    
    Flux complet:
    1. Enregistrer toutes les actions (InteractionLog)
    2. Extraire et mettre à jour les maîtrises de compétences (BKT)
    3. Calculer le score final de la session
    4. Mettre à jour l'état affectif
    5. Mettre à jour le comportement
    6. Générer une recommandation pédagogique
    7. Déterminer l'action suivante
    """
    # Vérifier que la session existe
    session = db.query(SimulationSession).filter(
        SimulationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Vérifier que la session n'est pas déjà terminée
    if session.statut == "termine":
        raise HTTPException(
            status_code=400,
            detail="Session déjà terminée"
        )
    
    try:
        result = process_simulation_completion(
            db,
            session_id,
            actions,
            diagnostic_propose,
            diagnostic_correct
        )
        
        return {
            "status": "success",
            "message": "Simulation traitée avec succès",
            "result": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement: {str(e)}"
        )


@router.get("/summary/{learner_id}")
def get_summary(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtenir un résumé complet de l'adaptation pour un apprenant.
    
    Inclut:
    - Modèle de connaissances (compétences maîtrisées)
    - Modèle de performances (scores, progression)
    - Modèle comportemental (engagement)
    - État affectif (motivation, frustration, etc.)
    - Statut global et recommandations
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    try:
        summary = get_adaptation_summary(db, learner_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du résumé: {str(e)}"
        )


@router.post("/batch-process")
def batch_process(
    simulations: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Traiter plusieurs simulations en batch.
    
    Format attendu pour chaque simulation:
    {
        "session_id": UUID,
        "actions": List[Dict],
        "diagnostic_propose": str,
        "diagnostic_correct": bool
    }
    """
    results = []
    successful = 0
    failed = 0
    
    for sim in simulations:
        try:
            session_id = UUID(sim.get("session_id"))
            actions = sim.get("actions", [])
            diagnostic_propose = sim.get("diagnostic_propose", "")
            diagnostic_correct = sim.get("diagnostic_correct", False)
            
            # Vérifier que la session existe
            session = db.query(SimulationSession).filter(
                SimulationSession.id == session_id
            ).first()
            
            if not session:
                results.append({
                    "status": "error",
                    "session_id": str(session_id),
                    "message": "Session non trouvée"
                })
                failed += 1
                continue
            
            # Traiter
            result = process_simulation_completion(
                db,
                session_id,
                actions,
                diagnostic_propose,
                diagnostic_correct
            )
            
            results.append({
                "status": "success",
                "session_id": str(session_id),
                "learner_id": result["learner_id"],
                "score_final": result["score_final"],
                "recommendation": result["recommendation"]
            })
            successful += 1
        
        except Exception as e:
            results.append({
                "status": "error",
                "session_id": sim.get("session_id", "unknown"),
                "message": str(e)
            })
            failed += 1
    
    return {
        "total": len(simulations),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@router.get("/recommendations/{learner_id}")
def get_recommendations(
    learner_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir des recommandations pédagogiques personnalisées."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    
    # Obtenir le résumé complet
    summary = get_adaptation_summary(db, learner_id)
    
    # Extraire les recommandations
    knowledge = summary.get("knowledge_model", {})
    performance = summary.get("performance_model", {})
    behavioral = summary.get("behavioral_model", {})
    affective = summary.get("affective_state", {})
    
    recommendations = []
    
    # Recommandations basées sur les compétences faibles
    avg_mastery = knowledge.get("average_mastery", 0)
    if avg_mastery < 0.5:
        recommendations.append({
            "type": "knowledge",
            "priority": "high",
            "message": "Renforcer les compétences de base avec des cas guidés"
        })
    
    # Recommandations basées sur les performances
    avg_score = performance.get("average_score", 0)
    trend = performance.get("trend", "stable")
    
    if avg_score < 50:
        recommendations.append({
            "type": "performance",
            "priority": "high",
            "message": "Revoir les fondamentaux et pratiquer sur des cas plus simples"
        })
    elif trend == "declining":
        recommendations.append({
            "type": "performance",
            "priority": "medium",
            "message": "Tendance à la baisse détectée. Faire une pause ou réviser les concepts"
        })
    
    # Recommandations basées sur le comportement
    engagement = behavioral.get("engagement_score", 0)
    if engagement < 0.3:
        recommendations.append({
            "type": "behavioral",
            "priority": "high",
            "message": "Engagement très faible. Proposer des activités plus motivantes"
        })
    
    # Recommandations basées sur l'affectif
    affective_label = affective.get("label", "")
    if "Négatif" in affective_label:
        recommendations.append({
            "type": "affective",
            "priority": "high",
            "message": "État émotionnel négatif. Fournir du soutien et encouragements"
        })
    
    return {
        "learner_id": learner_id,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations,
        "summary": {
            "average_mastery": avg_mastery,
            "average_score": avg_score,
            "engagement_score": engagement,
            "affective_state": affective_label
        }
    }


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Vérifier la santé du moteur d'adaptation."""
    try:
        # Tester la connexion DB
        db.execute("SELECT 1")
        
        # Compter les sessions actives
        active_sessions = db.query(SimulationSession).filter(
            SimulationSession.statut == "en_cours"
        ).count()
        
        # Compter les apprenants
        total_learners = db.query(Learner).count()
        
        return {
            "status": "healthy",
            "engine": "Adaptation Engine",
            "version": "1.0.0",
            "database": "connected",
            "active_sessions": active_sessions,
            "total_learners": total_learners,
            "message": "Moteur d'adaptation opérationnel"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Moteur d'adaptation indisponible: {str(e)}"
        )


# ============================================================================
### FICHIER 8: app/api/routes/performances.py
