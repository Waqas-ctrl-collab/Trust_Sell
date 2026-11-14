from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: str = Field(..., alias="_id")
    conversation_id: str
    sender_id: str
    sender_name: str
    text: str
    type: str = "sent"
    fraud_risk_score: float = 0.0
    fraud_flags: List[str] = []
    blocked: bool = False
    time: str = ""
    created_at: datetime

    class Config:
        populate_by_name = True


class ConversationCreate(BaseModel):
    participant_id: str
    listing_id: Optional[str] = None
    initial_message: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    avatar: str
    preview: str
    time: str
    listing_id: Optional[str] = None
    listing_title: Optional[str] = None
    participant_ids: List[str]

    class Config:
        populate_by_name = True
