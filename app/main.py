"""Point d'entrée FastAPI pour l'application STI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.models.learner import Learner
from app.models.learning_history import LearningHistory
from app.models.concept import Concept
from Backend.app.models.learner_competency_mastery import LearnerKnowledge
from app.models.learner_performance import LearnerPerformance
from app.models.learner_behavior import LearnerBehavior
from app.models.learner_cognitive import LearnerCognitiveProfile
from app.models.learner_affective import LearnerAffectiveState
from app.api.learners import router as learner_router
from app.api.learning_history import router as history_router
from app.api.concepts import router as concept_router
from app.api.learner_knowledge import router as knowledge_router
from app.api.learner_performance import router as performance_router
from app.api.learner_behavior import router as behavior_router
from app.api.learner_cognitive import router as cognitive_router
from app.api.learner_affective import router as affective_router
from app.api.adaptation import router as adaptation_router

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="Module apprenant sti",
    version="1.0.0",
    debug=True
)

# Ajouter les middlewares CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(learner_router)
app.include_router(history_router)
app.include_router(concept_router)
app.include_router(knowledge_router)
app.include_router(performance_router)
app.include_router(behavior_router)
app.include_router(cognitive_router)
app.include_router(affective_router)
app.include_router(adaptation_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
