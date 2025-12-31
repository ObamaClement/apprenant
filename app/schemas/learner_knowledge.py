"""Wrapper de compatibilité."""
from app.schemas.learner_competency import (
    LearnerCompetencyMasteryBase,
    LearnerCompetencyMasteryCreate,
    LearnerCompetencyMasteryUpdate,
    LearnerCompetencyMasteryResponse,
    LearnerCompetencyMasteryWithCompetence
)

# Aliases pour compatibilité
LearnerKnowledgeBase = LearnerCompetencyMasteryBase
LearnerKnowledgeCreate = LearnerCompetencyMasteryCreate
LearnerKnowledgeUpdate = LearnerCompetencyMasteryUpdate
LearnerKnowledgeResponse = LearnerCompetencyMasteryResponse