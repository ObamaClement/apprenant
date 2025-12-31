"""Schémas Pydantic - Imports centralisés."""

# Apprenant
from app.schemas.learner import (
    LearnerBase,
    LearnerCreate,
    LearnerUpdate,
    LearnerResponse
)

# Profil apprenant
from app.schemas.learner_behavior import (
    LearnerBehaviorBase,
    LearnerBehaviorCreate,
    LearnerBehaviorUpdate,
    LearnerBehaviorResponse
)

from app.schemas.learner_cognitive import (
    LearnerCognitiveBase,
    LearnerCognitiveCreate,
    LearnerCognitiveUpdate,
    LearnerCognitiveResponse
)

from app.schemas.learner_affective import (
    LearnerAffectiveBase,
    LearnerAffectiveCreate,
    LearnerAffectiveUpdate,
    LearnerAffectiveResponse
)

# Compétences
from app.schemas.competence_clinique import (
    CompetenceCliniqueBase,
    CompetenceCliniqueCreate,
    CompetenceCliniqueUpdate,
    CompetenceCliniqueResponse,
    CompetenceCliniqueWithPrerequisResponse
)

from app.schemas.prerequis_competence import (
    PrerequisCompetenceBase,
    PrerequisCompetenceCreate,
    PrerequisCompetenceUpdate,
    PrerequisCompetenceResponse,
    PrerequisCompetenceWithNames
)

from app.schemas.learner_competency import (
    LearnerCompetencyMasteryBase,
    LearnerCompetencyMasteryCreate,
    LearnerCompetencyMasteryUpdate,
    LearnerCompetencyMasteryResponse,
    LearnerCompetencyMasteryWithCompetence
)

# Sessions et interactions
from app.schemas.simulation_session import (
    SimulationSessionBase,
    SimulationSessionCreate,
    SimulationSessionUpdate,
    SimulationSessionComplete,
    SimulationSessionResponse,
    SimulationSessionWithDetails
)

from app.schemas.interaction_log import (
    InteractionLogBase,
    InteractionLogCreate,
    InteractionLogUpdate,
    InteractionLogResponse,
    InteractionLogWithContext,
    InteractionLogBatchCreate
)

# Contenu médical
from app.schemas.cas_clinique import (
    CasCliniqueBase,
    CasCliniqueCreate,
    CasCliniqueUpdate,
    CasCliniqueResponse,
    CasCliniqueListResponse
)

from app.schemas.pathologie import (
    PathologieBase,
    PathologieCreate,
    PathologieUpdate,
    PathologieResponse,
    PathologieListResponse
)

from app.schemas.symptome import (
    SymptomeBase,
    SymptomeCreate,
    SymptomeUpdate,
    SymptomeResponse
)

from app.schemas.medicament import (
    MedicamentBase,
    MedicamentCreate,
    MedicamentUpdate,
    MedicamentResponse,
    MedicamentListResponse
)

# Wrappers compatibilité
from app.schemas.learner_knowledge import (
    LearnerKnowledgeBase,
    LearnerKnowledgeCreate,
    LearnerKnowledgeUpdate,
    LearnerKnowledgeResponse
)

from app.schemas.concept import (
    ConceptBase,
    ConceptCreate,
    ConceptUpdate,
    ConceptResponse
)

__all__ = [
    # Apprenant
    "LearnerBase",
    "LearnerCreate",
    "LearnerUpdate",
    "LearnerResponse",
    
    # Profil apprenant
    "LearnerBehaviorBase",
    "LearnerBehaviorCreate",
    "LearnerBehaviorUpdate",
    "LearnerBehaviorResponse",
    "LearnerCognitiveBase",
    "LearnerCognitiveCreate",
    "LearnerCognitiveUpdate",
    "LearnerCognitiveResponse",
    "LearnerAffectiveBase",
    "LearnerAffectiveCreate",
    "LearnerAffectiveUpdate",
    "LearnerAffectiveResponse",
    
    # Compétences
    "CompetenceCliniqueBase",
    "CompetenceCliniqueCreate",
    "CompetenceCliniqueUpdate",
    "CompetenceCliniqueResponse",
    "CompetenceCliniqueWithPrerequisResponse",
    "PrerequisCompetenceBase",
    "PrerequisCompetenceCreate",
    "PrerequisCompetenceUpdate",
    "PrerequisCompetenceResponse",
    "PrerequisCompetenceWithNames",
    "LearnerCompetencyMasteryBase",
    "LearnerCompetencyMasteryCreate",
    "LearnerCompetencyMasteryUpdate",
    "LearnerCompetencyMasteryResponse",
    "LearnerCompetencyMasteryWithCompetence",
    
    # Sessions et interactions
    "SimulationSessionBase",
    "SimulationSessionCreate",
    "SimulationSessionUpdate",
    "SimulationSessionComplete",
    "SimulationSessionResponse",
    "SimulationSessionWithDetails",
    "InteractionLogBase",
    "InteractionLogCreate",
    "InteractionLogUpdate",
    "InteractionLogResponse",
    "InteractionLogWithContext",
    "InteractionLogBatchCreate",
    
    # Contenu médical
    "CasCliniqueBase",
    "CasCliniqueCreate",
    "CasCliniqueUpdate",
    "CasCliniqueResponse",
    "CasCliniqueListResponse",
    "PathologieBase",
    "PathologieCreate",
    "PathologieUpdate",
    "PathologieResponse",
    "PathologieListResponse",
    "SymptomeBase",
    "SymptomeCreate",
    "SymptomeUpdate",
    "SymptomeResponse",
    "MedicamentBase",
    "MedicamentCreate",
    "MedicamentUpdate",
    "MedicamentResponse",
    "MedicamentListResponse",
    
    # Compatibilité
    "LearnerKnowledgeBase",
    "LearnerKnowledgeCreate",
    "LearnerKnowledgeUpdate",
    "LearnerKnowledgeResponse",
    "ConceptBase",
    "ConceptCreate",
    "ConceptUpdate",
    "ConceptResponse",
]