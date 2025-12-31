"""Modèles SQLAlchemy - Version finale."""

# Modèles principaux STI
from app.models.learner import Learner
from app.models.competence_clinique import CompetenceClinique
from app.models.prerequis_competence import PrerequisCompetence
from app.models.learner_competency_mastery import LearnerCompetencyMastery
from app.models.simulation_session import SimulationSession
from app.models.interaction_log import InteractionLog
from app.models.cas_clinique import CasCliniqueEnrichi
from app.models.pathologie import Pathologie
from app.models.symptome import Symptome
from app.models.medicament import Medicament

# Profil apprenant
from app.models.learner_behavior import LearnerBehavior
from app.models.learner_cognitive import LearnerCognitiveProfile
from app.models.learner_affective import LearnerAffectiveState

# Wrappers compatibilité
from app.models.learner_knowledge import LearnerKnowledge
from app.models.concept import Concept

__all__ = [
    # Principaux
    "Learner",
    "CompetenceClinique",
    "PrerequisCompetence",
    "LearnerCompetencyMastery",
    "SimulationSession",
    "InteractionLog",
    "CasCliniqueEnrichi",
    "Pathologie",
    "Symptome",
    "Medicament",
    
    # Profil
    "LearnerBehavior",
    "LearnerCognitiveProfile",
    "LearnerAffectiveState",
    
    # Compatibilité
    "LearnerKnowledge",
    "Concept",
]