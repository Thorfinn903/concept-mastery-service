from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

# Input: The Event data coming from Service 1
class EventIncoming(BaseModel):
    user_id: str
    concept_id: str
    event_type: str
    event_details: Dict[str, Any] = {}

# Output: What we show the user
class MasteryResponse(BaseModel):
    user_id: str
    concept_id: str
    mastery_score: float
    total_attempts: int
    successful_attempts: int
    last_updated: datetime

    # strict configuration
    model_config = ConfigDict(from_attributes=True)