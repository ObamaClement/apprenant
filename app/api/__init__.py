# ============================================================================
### FICHIER 14: app/api/routes/__init__.py (MISE À JOUR COMPLÈTE)
"""Initialisation des routes API - VERSION COMPLÈTE STI."""
from fastapi import APIRouter

# Core - Apprenants
from app.api import learners

# Compétences cliniques
from app.api import competences
from app.api import prerequis_competences
from app.api import learner_competency_mastery

# Sessions et interactions (CRITIQUE)
from app.api import simulation_sessions
from app.api import interaction_logs
from app.api import cas_cliniques

# Profils apprenants
from app.api import learner_behavior
from app.api import learner_cognitive
from app.api import learner_affective

# Performances et connaissances
from app.api import performances
from app.api import knowledge_inference

# Adaptation intelligente (CRITIQUE)
from app.api import adaptation_engine

# Contenu médical
from app.api import pathologies
from app.api import symptomes
from app.api import medicaments


# Router principal
api_router = APIRouter()

# ============================================================================
# GROUPE 1: CORE - Gestion des apprenants
# ============================================================================
api_router.include_router(
    learners.router,
    tags=["Learners"]
)

# ============================================================================
# GROUPE 2: COMPÉTENCES CLINIQUES
# ============================================================================
api_router.include_router(
    competences.router,
    tags=["Clinical Competencies"]
)

api_router.include_router(
    prerequis_competences.router,
    tags=["Competency Prerequisites"]
)

api_router.include_router(
    learner_competency_mastery.router,
    tags=["Competency Mastery"]
)

# ============================================================================
# GROUPE 3: SIMULATIONS (CRITIQUE)
# ============================================================================
api_router.include_router(
    simulation_sessions.router,
    tags=["Simulation Sessions"]
)

api_router.include_router(
    interaction_logs.router,
    tags=["Interaction Logs"]
)

api_router.include_router(
    cas_cliniques.router,
    tags=["Clinical Cases"]
)

# ============================================================================
# GROUPE 4: PROFILS APPRENANTS
# ============================================================================
api_router.include_router(
    learner_behavior.router,
    tags=["Learner Behavior"]
)

api_router.include_router(
    learner_cognitive.router,
    tags=["Learner Cognitive"]
)

api_router.include_router(
    learner_affective.router,
    tags=["Learner Affective"]
)

# ============================================================================
# GROUPE 5: ANALYTICS & ADAPTATION (CRITIQUE)
# ============================================================================
api_router.include_router(
    performances.router,
    tags=["Performance Analytics"]
)

api_router.include_router(
    knowledge_inference.router,
    tags=["Knowledge Inference"]
)

api_router.include_router(
    adaptation_engine.router,
    tags=["Adaptation Engine"]
)

# ============================================================================
# GROUPE 6: CONTENU MÉDICAL
# ============================================================================
api_router.include_router(
    pathologies.router,
    tags=["Pathologies"]
)

api_router.include_router(
    symptomes.router,
    tags=["Symptoms"]
)

api_router.include_router(
    medicaments.router,
    tags=["Medications"]
)


# ============================================================================
# ENDPOINTS DE BASE (Health & Info)
# ============================================================================
@api_router.get("/", tags=["Root"])
def root():
    """Endpoint racine de l'API."""
    return {
        "message": "STI Backend API",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs"
    }


@api_router.get("/health", tags=["Health"])
def health_check():
    """Vérifier la santé de l'API."""
    return {
        "status": "healthy",
        "api": "STI Backend",
        "version": "2.0.0"
    }


@api_router.get("/routes", tags=["Info"])
def list_routes():
    """Lister toutes les routes disponibles."""
    return {
        "core": {
            "learners": "/learners"
        },
        "competencies": {
            "competences": "/competences",
            "prerequis": "/prerequis",
            "mastery": "/mastery"
        },
        "simulations": {
            "sessions": "/sessions",
            "interactions": "/interactions",
            "cases": "/cases"
        },
        "profiles": {
            "behavior": "/behavior",
            "cognitive": "/cognitive",
            "affective": "/affective"
        },
        "analytics": {
            "performances": "/performances",
            "knowledge": "/knowledge",
            "adaptation": "/adaptation"
        },
        "medical_content": {
            "pathologies": "/pathologies",
            "symptomes": "/symptomes",
            "medicaments": "/medicaments"
        }
    }