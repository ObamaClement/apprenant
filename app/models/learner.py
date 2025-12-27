from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Learner(Base):
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    level = Column(String(50), nullable=True)
    field_of_study = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learning_histories = relationship(
        "LearningHistory",
        back_populates="learner",
        cascade="all, delete"
    )

    knowledge = relationship(
        "LearnerKnowledge",
        back_populates="learner",
        cascade="all, delete"
    )
