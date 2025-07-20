from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ChatSessionBase(BaseModel):
    user_id: UUID
    session_name: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    session_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    message_count: int
    
    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    session_id: UUID
    user_id: UUID
    message_type: str
    content: str
    intent: Optional[str] = None
    action_taken: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    message_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True