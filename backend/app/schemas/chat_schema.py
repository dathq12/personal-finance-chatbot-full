# schemas/chatbot_schema.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"

class Intent(str, Enum):
    ADD_TRANSACTION = "add_transaction"
    GET_BALANCE = "get_balance"
    GET_SPENDING = "get_spending"
    BUDGET_ADVICE = "budget_advice"
    GENERAL_QUERY = "general_query"
    GREETING = "greeting"
    GOODBYE = "goodbye"

class ActionType(str, Enum):
    TRANSACTION_CREATED = "transaction_created"
    BALANCE_RETRIEVED = "balance_retrieved"
    ADVICE_GIVEN = "advice_given"
    NO_ACTION = "no_action"

# Chat Session Schemas
class ChatSessionBase(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255, description="Optional name for the chat session")

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    ended_at: Optional[datetime] = None

class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    SessionID: UUID
    UserID: UUID
    session_name: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    message_count: int
    created_at: Optional[datetime] = None

# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")
    message_type: MessageType = Field(..., description="Type of message")
    intent: Optional[Intent] = Field(None, description="Detected intent")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities from the message")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for intent detection")
    action_taken: Optional[ActionType] = Field(None, description="Action taken based on the message")

class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000, description="User message content")

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    MessageID: UUID
    SessionID: UUID
    UserID: UUID
    message_type: str
    content: str
    intent: Optional[str] = None
    entities: Optional[str] = None  # JSON string in database
    confidence_score: Optional[float] = None
    action_taken: Optional[str] = None
    created_at: datetime

# Chat Conversation Schemas
class ChatConversationResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse] = Field(..., description="List of messages in the conversation")

class ChatInteractionRequest(BaseModel):
    session_id: Optional[UUID] = Field(None, description="Existing session ID, if continuing conversation")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_name: Optional[str] = Field(None, max_length=255, description="Session name for new sessions")

class ChatInteractionResponse(BaseModel):
    session_id: UUID
    user_message: ChatMessageResponse
    bot_response: ChatMessageResponse
    session_info: ChatSessionResponse
    action_performed: Optional[Dict[str, Any]] = Field(None, description="Details of any action performed")

# Filter and List Schemas
class ChatSessionFilter(BaseModel):
    is_active: Optional[bool] = Field(None, description="Filter by active sessions")
    date_from: Optional[datetime] = Field(None, description="Filter sessions started from this date")
    date_to: Optional[datetime] = Field(None, description="Filter sessions started before this date")
    session_name: Optional[str] = Field(None, description="Search by session name")
    
    # Pagination
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of records to return")
    
    # Sorting
    sort_by: Optional[str] = Field("started_at", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort direction: 'asc' or 'desc'")

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v

class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse] = Field(..., description="List of chat sessions")
    total_count: int = Field(..., description="Total number of sessions")

# Analytics Schemas
class ChatAnalyticsResponse(BaseModel):
    total_sessions: int
    active_sessions: int
    total_messages: int
    average_messages_per_session: float
    most_common_intents: List[Dict[str, Any]]
    actions_performed: Dict[str, int]
    session_duration_stats: Dict[str, float]  # avg, min, max duration in minutes

# Transaction Integration Schema
class TransactionFromChatRequest(BaseModel):
    transaction_type: str = Field(..., description="Type of transaction: 'income' or 'expense'")
    amount: float = Field(..., gt=0, description="Transaction amount")
    description: Optional[str] = Field(None, max_length=500)
    category_display_name: str = Field(..., description="Category name")
    payment_method: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field("Created via chatbot", max_length=500)
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        if v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower()