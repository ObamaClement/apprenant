"""Schémas Pydantic pour le profil cognitif de l'apprenant."""
from pydantic import BaseModel, Field
from typing import Optional


class LearnerCognitiveBase(BaseModel):
    """Schéma de base pour le profil cognitif."""
    learner_id: int
    vitesse_assimilation: Optional[float] = Field(None, ge=0.0, le=1.0)
    capacite_memoire_travail: Optional[float] = Field(None, ge=0.0, le=1.0)
    tendance_impulsivite: Optional[float] = Field(None, ge=0.0, le=1.0)
    prefer_visual: Optional[bool] = None


class LearnerCognitiveCreate(LearnerCognitiveBase):
    """Schéma pour créer un profil cognitif."""
    pass


class LearnerCognitiveUpdate(BaseModel):
    """Schéma pour mettre à jour un profil cognitif."""
    vitesse_assimilation: Optional[float] = Field(None, ge=0.0, le=1.0)
    capacite_memoire_travail: Optional[float] = Field(None, ge=0.0, le=1.0)
    tendance_impulsivite: Optional[float] = Field(None, ge=0.0, le=1.0)
    prefer_visual: Optional[bool] = None


class LearnerCognitiveResponse(LearnerCognitiveBase):
    """Schéma de réponse pour le profil cognitif."""
    id: int
    
    # Propriétés de compatibilité
    @property
    def learning_style(self) -> Optional[str]:
        if self.prefer_visual is True:
            return "visuel"
        elif self.prefer_visual is False:
            return "auditif"
        return None
    
    @property
    def learning_speed(self) -> Optional[float]:
        return self.vitesse_assimilation
    
    @property
    def autonomy_level(self) -> Optional[float]:
        if self.tendance_impulsivite is not None:
            return 1.0 - self.tendance_impulsivite
        return None

    class Config:
        from_attributes = True