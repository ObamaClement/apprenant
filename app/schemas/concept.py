"""Wrapper de compatibilité."""
from app.schemas.competence_clinique import (
    CompetenceCliniqueBase,
    CompetenceCliniqueCreate,
    CompetenceCliniqueUpdate,
    CompetenceCliniqueResponse,
    CompetenceCliniqueWithPrerequisResponse
)

# Aliases pour compatibilité
ConceptBase = CompetenceCliniqueBase
ConceptCreate = CompetenceCliniqueCreate
ConceptUpdate = CompetenceCliniqueUpdate
ConceptResponse = CompetenceCliniqueResponse