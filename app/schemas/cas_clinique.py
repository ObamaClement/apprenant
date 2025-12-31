"""Schémas Pydantic pour les cas cliniques."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal


class CasCliniqueBase(BaseModel):
    """Schéma de base pour un cas clinique."""
    code_fultang: Optional[str] = None
    pathologie_principale_id: Optional[int] = None
    presentation_clinique: Dict[str, Any]
    donnees_paracliniques: Optional[Dict[str, Any]] = None
    niveau_difficulte: Optional[int] = Field(None, ge=1, le=5)
    duree_estimee_resolution_min: Optional[int] = None
    objectifs_apprentissage: Optional[Dict[str, Any]] = None
    competences_requises: Optional[Dict[str, Any]] = None


class CasCliniqueCreate(CasCliniqueBase):
    """Schéma pour créer un cas clinique."""
    pass


class CasCliniqueUpdate(BaseModel):
    """Schéma pour mettre à jour un cas clinique."""
    presentation_clinique: Optional[Dict[str, Any]] = None
    donnees_paracliniques: Optional[Dict[str, Any]] = None
    niveau_difficulte: Optional[int] = Field(None, ge=1, le=5)
    duree_estimee_resolution_min: Optional[int] = None
    valide_expert: Optional[bool] = None
    qualite_donnees: Optional[int] = None


class CasCliniqueResponse(CasCliniqueBase):
    """Schéma de réponse pour un cas clinique."""
    id: int
    hash_integrite: Optional[str] = None
    evolution_patient: Optional[str] = None
    images_associees_ids: Optional[List[int]] = None
    medicaments_prescrits: Optional[Dict[str, Any]] = None
    valide_expert: Optional[bool] = None
    date_validation: Optional[date] = None
    qualite_donnees: Optional[int] = None
    nb_utilisations: Optional[int] = None
    note_moyenne_apprenants: Optional[Decimal] = None
    taux_succes_diagnostic: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    pathologies_secondaires_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


# Schéma simplifié pour liste
class CasCliniqueListResponse(BaseModel):
    """Schéma simplifié pour liste de cas."""
    id: int
    code_fultang: Optional[str] = None
    pathologie_principale_id: Optional[int] = None
    niveau_difficulte: Optional[int] = None
    duree_estimee_resolution_min: Optional[int] = None
    valide_expert: Optional[bool] = None
    nb_utilisations: Optional[int] = None
    note_moyenne_apprenants: Optional[Decimal] = None
    
    class Config:
        from_attributes = True