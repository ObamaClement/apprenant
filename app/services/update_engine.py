"""Moteur de mise à jour pour les apprenants (IA / règles)."""
from sqlalchemy.orm import Session
from app.models.learner import Learner
from app.models.performance import Performance


class UpdateEngine:
    """Moteur pour mettre à jour les profils d'apprenants basé sur les performances et états affectifs."""
    
    @staticmethod
    def update_learner_progress(db: Session, learner_id: int) -> float:
        """Calculer et mettre à jour la progression d'un apprenant."""
        performances = db.query(Performance).filter(
            Performance.learner_id == learner_id
        ).all()
        
        if not performances:
            return 0.0
        
        total_score = sum(p.score for p in performances)
        average_score = total_score / len(performances)
        
        learner = db.query(Learner).filter(Learner.id == learner_id).first()
        if learner:
            learner.progress = average_score
            db.commit()
        
        return average_score
    
    @staticmethod
    def adjust_difficulty(db: Session, learner_id: int) -> str:
        """Ajuster le niveau de difficulté basé sur les performances."""
        learner = db.query(Learner).filter(Learner.id == learner_id).first()
        if not learner:
            return "beginner"
        
        progress = UpdateEngine.update_learner_progress(db, learner_id)
        
        if progress >= 0.8:
            new_level = "advanced"
        elif progress >= 0.6:
            new_level = "intermediate"
        else:
            new_level = "beginner"
        
        learner.level = new_level
        db.commit()
        
        return new_level
