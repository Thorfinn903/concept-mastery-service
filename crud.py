from sqlalchemy.orm import Session
import db_models as models  # <--- THIS IS THE KEY TRICK
import datetime

def get_mastery(db: Session, user_id: str, concept_id: str):
    return db.query(models.ConceptMastery).filter(
        models.ConceptMastery.user_id == user_id,
        models.ConceptMastery.concept_id == concept_id
    ).first()


def get_all_mastery(db: Session, user_id: str):
    return db.query(models.ConceptMastery).filter(models.ConceptMastery.user_id == user_id).all()


def update_mastery_from_event(db: Session, user_id: str, concept_id: str, event_type: str, score: int):
    # Find existing record or make a new one
    record = get_mastery(db, user_id, concept_id)

    if not record:
        record = models.ConceptMastery(
            user_id=user_id,
            concept_id=concept_id,
            total_attempts=0,
            successful_attempts=0,
            mastery_score=0.0
        )
        db.add(record)

    # Logic: Only update if it's a quiz
    if event_type == "quiz_attempt":
        record.total_attempts += 1

        # Threshold logic: Score >= 60 is a success
        # (Assuming score is out of 100)
        if score >= 60:
            record.successful_attempts += 1

        #  Recalculate Mastery
        if record.total_attempts > 0:
            record.mastery_score = record.successful_attempts / record.total_attempts

        record.last_updated = datetime.datetime.utcnow()
        db.commit()
        db.refresh(record)

    return record