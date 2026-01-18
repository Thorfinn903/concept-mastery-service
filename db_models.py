from sqlalchemy import Column, String, Float, Integer, DateTime
import datetime
from database import Base


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    user_id = Column(String, primary_key=True)
    concept_id = Column(String, primary_key=True)

    mastery_score = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
