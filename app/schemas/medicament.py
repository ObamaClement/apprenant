"""Schémas Pydantic pour les médicaments."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MedicamentBase(BaseModel):
    """Schéma de base pour un médicament."""
    nom_commercial: Optional[str] = None
    dci: str
    classe_therapeutique: Optional[str] = None
    forme_galenique: Optional[str] = None
    dosage: Optional[str] = None
    voie_administration: Optional[str] = None


class MedicamentCreate(MedicamentBase):
    """Schéma pour créer un médicament."""
    pass


class MedicamentUpdate(BaseModel):
    """Schéma pour mettre à jour un médicament."""
    nom_commercial: Optional[str] = None
    classe_therapeutique: Optional[str] = None
    forme_galenique: Optional[str] = None
    dosage: Optional[str] = None
    disponibilite_cameroun: Optional[str] = None
    cout_moyen_fcfa: Optional[int] = None


class MedicamentResponse(MedicamentBase):
    """Schéma de réponse pour un médicament."""
    id: int
    mecanisme_action: Optional[str] = None
    indications: Optional[Dict[str, Any]] = None
    contre_indications: Optional[Dict[str, Any]] = None
    effets_secondaires: Optional[Dict[str, Any]] = None
    interactions_medicamenteuses: Optional[Dict[str, Any]] = None
    precautions_emploi: Optional[str] = None
    posologie_standard: Optional[Dict[str, Any]] = None
    disponibilite_cameroun: Optional[str] = None
    cout_moyen_fcfa: Optional[int] = None
    statut_prescription: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schéma simplifié
class MedicamentListResponse(BaseModel):
    """Schéma simplifié pour liste."""
    id: int
    nom_commercial: Optional[str] = None
    dci: str
    classe_therapeutique: Optional[str] = None
    disponibilite_cameroun: Optional[str] = None
    cout_moyen_fcfa: Optional[int] = None
    
    class Config:
        from_attributes = True