"""Service métier pour les apprenants."""
from sqlalchemy.orm import Session
from app.models.learner import Learner
from app.schemas.learner import LearnerCreate, LearnerUpdate


class LearnerService:
    """Service pour gérer les apprenants."""
    
    @staticmethod
    def create_learner(db: Session, learner: LearnerCreate) -> Learner:
        """Créer un nouvel apprenant."""
        db_learner = Learner(**learner.dict())
        db.add(db_learner)
        db.commit()
        db.refresh(db_learner)
        return db_learner
    
    @staticmethod
    def get_learner(db: Session, learner_id: int) -> Learner:
        """Récupérer un apprenant par ID."""
        return db.query(Learner).filter(Learner.id == learner_id).first()
    
    @staticmethod
    def get_learners(db: Session, skip: int = 0, limit: int = 10) -> list[Learner]:
        """Récupérer la liste des apprenants."""
        return db.query(Learner).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_learner(db: Session, learner_id: int, learner_update: LearnerUpdate) -> Learner:
        """Mettre à jour un apprenant."""
        db_learner = db.query(Learner).filter(Learner.id == learner_id).first()
        if db_learner:
            update_data = learner_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_learner, field, value)
            db.commit()
            db.refresh(db_learner)
        return db_learner
    
    @staticmethod
    def delete_learner(db: Session, learner_id: int) -> bool:
        """Supprimer un apprenant."""
        db_learner = db.query(Learner).filter(Learner.id == learner_id).first()
        if db_learner:
            db.delete(db_learner)
            db.commit()
            return True
        return False
