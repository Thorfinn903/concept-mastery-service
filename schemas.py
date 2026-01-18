from pydantic import BaseModel
from datetime import datetime

# Input: The Event data coming from Service 1
class EventIncoming(BaseModel):
    user_id: str
    concept_id: str
    event_type: str
    event_details: dict = {}

# Output: What we show the user
class MasteryResponse(BaseModel):
    user_id: str
    concept_id: str
    mastery_score: float
    total_attempts: int
    successful_attempts: int
    last_updated: datetime

    class Config:
        from_attributes = True