from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests  # <--- New library to talk to Service 1
from database import engine, get_db, Base

import db_models
import schemas
import crud
from database import engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

# URL of your FIRST service (The Logger)
# Note: It runs on port 8000
LEARNING_EVENTS_SERVICE_URL = "http://127.0.0.1:8000"


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
    # Step A: Call Service 1 API
    try:
        response = requests.get(f"{LEARNING_EVENTS_SERVICE_URL}/events/{user_id}")
        events = response.json()  # Convert list of events to Python list
    except:
        raise HTTPException(status_code=500, detail="Could not connect to Learning Events Service")

    # Step B: Reset current mastery for this user (Simple Logic: just loop and update)
    # Ideally, we would wipe data first, but let's just re-process for now.

    count = 0
    for event in events:
        # Extract data from the event list
        e_type = event['event_type']
        c_id = event['concept_id']
        details = event['event_details']
        score = details.get('score', 0)

        crud.update_mastery_from_event(db, user_id, c_id, e_type, score)
        count += 1

    return {"message": f"Successfully reprocessed {count} events for {user_id}"}