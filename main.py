from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests  # <--- New library to talk to Service 1
from database import engine, get_db, Base  # noqa: F401  (engine and get_db are used by metadata and dependencies)

import db_models  # noqa: F401  (models are imported for SQLAlchemy metadata)
import schemas
import crud

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

Base.metadata.create_all(bind=engine)

app = FastAPI()

# URL of your FIRST service (The Logger)
# Note: It runs on port 8000
LEARNING_EVENTS_SERVICE_URL = "http://127.0.0.1:8000"


def _make_session(retries: int = 3, backoff_factor: float = 0.5, timeout: int = 5):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.request = lambda *args, **kwargs: requests.Session.request(session, *args, timeout=timeout, **kwargs)
    return session


@app.get("/")
def home():
    return {"message": "Concept Mastery Service is running on Port 8001"}


# 1. Get Mastery for a User
@app.get("/mastery/{user_id}", response_model=List[schemas.MasteryResponse])
def get_user_mastery(user_id: str, db: Session = Depends(get_db)):
    return crud.get_all_mastery(db, user_id)


# 2. Get Mastery for a specific Concept
@app.get("/mastery/{user_id}/{concept_id}", response_model=schemas.MasteryResponse)
def get_concept_mastery(user_id: str, concept_id: str, db: Session = Depends(get_db)):
    record = crud.get_mastery(db, user_id, concept_id)
    if not record:
        raise HTTPException(status_code=404, detail="No mastery record found")
    return record


# 3. Receive an Event (Webhook style) - For real-time updates
@app.post("/process_event")
def process_event(event: schemas.EventIncoming, db: Session = Depends(get_db)):
    # Extract score safely
    score = event.event_details.get("score", 0)

    updated_record = crud.update_mastery_from_event(
        db, event.user_id, event.concept_id, event.event_type, score
    )
    return {"status": "updated", "new_mastery": updated_record.mastery_score}


# 4. Recompute Everything (The Advanced Feature)
@app.post("/mastery/recompute/{user_id}")
def recompute_mastery(user_id: str, db: Session = Depends(get_db)):
    """
    Connects to Service 1, gets all history, and recalculates mastery from scratch.
    """
    # Build a resilient HTTP session
    session = _make_session()

    # Step A: Call Service 1 API
    try:
        resp = session.get(f"{LEARNING_EVENTS_SERVICE_URL}/events/{user_id}")
        resp.raise_for_status()
        events = resp.json()
        if not isinstance(events, list):
            raise ValueError("Events payload is not a list")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not fetch events: {exc}")

    # Step B: Batch update within a single DB transaction where possible
    processed = 0
    skipped = 0

    try:
        # Use the provided db session and avoid committing per event; commit once at the end
        for ev in events:
            # Quick validation and normalization
            try:
                # Allow dict-like input to be validated by Pydantic
                incoming = schemas.EventIncoming(**ev) if isinstance(ev, dict) else None
                if incoming is None:
                    skipped += 1
                    continue
            except Exception:
                skipped += 1
                continue

            score = incoming.event_details.get("score", 0)
            crud.update_mastery_from_event(db, incoming.user_id, incoming.concept_id, incoming.event_type, score, commit=False)
            processed += 1

        # Commit once after batch
        db.commit()
    except Exception as exc:
        # Rollback on any unexpected error
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed while processing events: {exc}")

    return {"message": f"Successfully processed {processed} events, skipped {skipped} events for {user_id}"}
