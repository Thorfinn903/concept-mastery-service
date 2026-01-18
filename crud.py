from sqlalchemy.orm import Session
import db_models as models
import datetime
from typing import List, Dict, Any


# --- READ OPERATIONS ---

def get_mastery(db: Session, user_id: str, concept_id: str):
    return db.query(models.ConceptMastery).filter(
        models.ConceptMastery.user_id == user_id,
        models.ConceptMastery.concept_id == concept_id
    ).first()


def get_all_mastery(db: Session, user_id: str):
    return db.query(models.ConceptMastery).filter(models.ConceptMastery.user_id == user_id).all()


# --- WRITE OPERATIONS ---

def update_mastery_from_event(
        db: Session,
        user_id: str,
        concept_id: str,
        event_type: str,
        score: int,
        commit: bool = True
):
    # Find existing or create new
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

    # Logic
    if event_type == "quiz_attempt":
        record.total_attempts += 1
        if score >= 60:
            record.successful_attempts += 1

        if record.total_attempts > 0:
            record.mastery_score = record.successful_attempts / record.total_attempts

        # Use timezone-aware UTC
        record.last_updated = datetime.datetime.now(datetime.timezone.utc)


        if commit:
            db.commit()
            db.refresh(record)

    return record



def batch_update_mastery(db: Session, user_id: str, events: List[Dict[str, Any]]) -> int:
    processed_count = 0
    for event in events:

        update_mastery_from_event(
            db,
            user_id,
            event.get('concept_id'),
            event.get('event_type'),
            event.get('event_details', {}).get('score', 0),
            commit=False
        )
        processed_count += 1

    # Single commit at the end
    db.commit()
    return processed_count