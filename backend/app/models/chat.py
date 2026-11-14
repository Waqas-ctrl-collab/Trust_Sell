from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageDB(BaseModel):
    conversation_id: str
    sender_id: str
    sender_name: str
    text: str
    fraud_risk_score: float = 0.0
    fraud_flags: List[str] = Field(default_factory=list)
    blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "text": self.text,
            "fraud_risk_score": self.fraud_risk_score,
            "fraud_flags": self.fraud_flags,
            "blocked": self.blocked,
            "created_at": self.created_at,
        }


class ConversationDB(BaseModel):
    participant_ids: List[str]
    participant_names: List[str]
    listing_id: Optional[str] = None
    listing_title: Optional[str] = None
    last_message: str = ""
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "participant_ids": self.participant_ids,
            "participant_names": self.participant_names,
            "listing_id": self.listing_id,
            "listing_title": self.listing_title,
            "last_message": self.last_message,
            "last_message_at": self.last_message_at,
            "created_at": self.created_at,
        }
