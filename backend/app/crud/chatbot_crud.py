# crud/chatbot_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, case
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
import json
from fastapi import HTTPException, status

from models.chat import ChatSession, ChatMessage
from schemas.chat_schema import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionFilter,
    ChatSessionListResponse,
    ChatConversationResponse,
    MessageType,
    Intent,
    ActionType,
    ChatAnalyticsResponse
)

# Chat Session CRUD Operations
def create_chat_session(
    db: Session,
    user_id: UUID,
    session_data: ChatSessionCreate
) -> ChatSessionResponse:
    """Create a new chat session"""
    db_session = ChatSession(
        UserID=user_id,
        SessionName=session_data.session_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return ChatSessionResponse(
        SessionID=db_session.SessionID,
        UserID=db_session.UserID,
        session_name=db_session.SessionName,
        started_at=db_session.StartedAt,
        ended_at=db_session.EndedAt,
        is_active=db_session.IsActive,
        message_count=db_session.MessageCount
    )

def get_chat_session_by_id(
    db: Session,
    user_id: UUID,
    session_id: UUID
) -> Optional[ChatSessionResponse]:
    """Get a chat session by ID"""
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.SessionID == session_id,
            ChatSession.UserID == user_id
        )
        .first()
    )
    
    if not session:
        return None

    return ChatSessionResponse(
        SessionID=session.SessionID,
        UserID=session.UserID,
        session_name=session.SessionName,
        started_at=session.StartedAt,
        ended_at=session.EndedAt,
        is_active=session.IsActive,
        message_count=session.MessageCount
    )

def get_chat_sessions(
    db: Session,
    user_id: UUID,
    filters: ChatSessionFilter
) -> ChatSessionListResponse:
    """Get chat sessions with filters"""
    query = db.query(ChatSession).filter(ChatSession.UserID == user_id)
    
    # Apply filters
    if filters.is_active is not None:
        query = query.filter(ChatSession.IsActive == filters.is_active)
    
    if filters.date_from:
        query = query.filter(ChatSession.StartedAt >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(ChatSession.StartedAt <= filters.date_to)
    
    if filters.session_name:
        query = query.filter(ChatSession.SessionName.ilike(f"%{filters.session_name}%"))
    
    # Count total sessions
    total_count = query.count()
    
    # Apply sorting
    sort_field = getattr(ChatSession, filters.sort_by, ChatSession.StartedAt)
    if filters.sort_order == 'desc':
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Apply pagination
    query = query.offset(filters.skip).limit(filters.limit)
    
    results = query.all()
    
    sessions = []
    for session in results:
        sessions.append(ChatSessionResponse(
            SessionID=session.SessionID,
            UserID=session.UserID,
            session_name=session.SessionName,
            started_at=session.StartedAt,
            ended_at=session.EndedAt,
            is_active=session.IsActive,
            message_count=session.MessageCount
        ))
    
    return ChatSessionListResponse(
        sessions=sessions,
        total_count=total_count
    )

def update_chat_session(
    db: Session,
    user_id: UUID,
    session_id: UUID,
    session_data: ChatSessionUpdate
) -> Optional[ChatSessionResponse]:
    """Update a chat session"""
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.SessionID == session_id,
            ChatSession.UserID == user_id
        )
        .first()
    )
    
    if not session:
        return None
    
    update_data = session_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'session_name':
            setattr(session, 'SessionName', value)
        elif key == 'is_active':
            setattr(session, 'IsActive', value)
        elif key == 'ended_at':
            setattr(session, 'EndedAt', value)
    
    db.commit()
    db.refresh(session)
    
    return ChatSessionResponse(
        SessionID=session.SessionID,
        UserID=session.UserID,
        session_name=session.SessionName,
        started_at=session.StartedAt,
        ended_at=session.EndedAt,
        is_active=session.IsActive,
        message_count=session.MessageCount
    )

def end_chat_session(
    db: Session,
    user_id: UUID,
    session_id: UUID
) -> Optional[ChatSessionResponse]:
    """End a chat session"""
    return update_chat_session(
        db, user_id, session_id,
        ChatSessionUpdate(is_active=False, ended_at=datetime.utcnow())
    )

# Chat Message CRUD Operations
def create_chat_message(
    db: Session,
    session_id: UUID,
    user_id: UUID,
    message_type: MessageType,
    content: str,
    intent: Optional[Intent] = None,
    entities: Optional[Dict[str, Any]] = None,
    confidence_score: Optional[float] = None,
    action_taken: Optional[ActionType] = None
) -> ChatMessageResponse:
    """Create a new chat message"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.SessionID == session_id,
        ChatSession.UserID == user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db_message = ChatMessage(
        SessionID=session_id,
        UserID=user_id,
        MessageType=message_type.value,
        Content=content,
        Intent=intent.value if intent else None,
        Entities=json.dumps(entities) if entities else None,
        ConfidenceScore=confidence_score,
        ActionTaken=action_taken.value if action_taken else None
    )
    
    db.add(db_message)
    
    # Update session message count
    session.MessageCount = session.MessageCount + 1
    
    db.commit()
    db.refresh(db_message)
    
    return ChatMessageResponse(
        MessageID=db_message.MessageID,
        SessionID=db_message.SessionID,
        UserID=db_message.UserID,
        message_type=db_message.MessageType,
        content=db_message.Content,
        intent=db_message.Intent,
        entities=db_message.Entities,
        confidence_score=db_message.ConfidenceScore,
        action_taken=db_message.ActionTaken,
        created_at=db_message.CreatedAt
    )

def get_chat_messages(
    db: Session,
    session_id: UUID,
    user_id: UUID,
    limit: int = 50
) -> List[ChatMessageResponse]:
    """Get messages for a chat session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.SessionID == session_id,
        ChatSession.UserID == user_id
    ).first()
    
    if not session:
        return []
    
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.SessionID == session_id)
        .order_by(ChatMessage.CreatedAt)
        .limit(limit)
        .all()
    )
    
    return [
        ChatMessageResponse(
            MessageID=msg.MessageID,
            SessionID=msg.SessionID,
            UserID=msg.UserID,
            message_type=msg.MessageType,
            content=msg.Content,
            intent=msg.Intent,
            entities=msg.Entities,
            confidence_score=msg.ConfidenceScore,
            action_taken=msg.ActionTaken,
            created_at=msg.CreatedAt
        )
        for msg in messages
    ]

def get_conversation(
    db: Session,
    session_id: UUID,
    user_id: UUID
) -> Optional[ChatConversationResponse]:
    """Get full conversation (session + messages)"""
    session = get_chat_session_by_id(db, user_id, session_id)
    if not session:
        return None
    
    messages = get_chat_messages(db, session_id, user_id)
    
    return ChatConversationResponse(
        session=session,
        messages=messages
    )

def delete_chat_session(
    db: Session,
    user_id: UUID,
    session_id: UUID
) -> bool:
    """Delete a chat session and all its messages"""
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.SessionID == session_id,
            ChatSession.UserID == user_id
        )
        .first()
    )
    
    if not session:
        return False
    
    # Messages will be deleted automatically due to cascade
    db.delete(session)
    db.commit()
    return True

# Analytics Functions
def get_chat_analytics(
    db: Session,
    user_id: UUID,
    days_back: int = 30
) -> ChatAnalyticsResponse:
    """Get chat analytics for user"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Basic stats
    total_sessions = db.query(ChatSession).filter(ChatSession.UserID == user_id).count()
    active_sessions = db.query(ChatSession).filter(
        ChatSession.UserID == user_id,
        ChatSession.IsActive == True
    ).count()
    
    total_messages = db.query(ChatMessage).filter(
        ChatMessage.UserID == user_id,
        ChatMessage.CreatedAt >= cutoff_date
    ).count()
    
    # Average messages per session
    avg_messages = (
        db.query(func.avg(ChatSession.MessageCount))
        .filter(ChatSession.UserID == user_id)
        .scalar()
    ) or 0
    
    # Most common intents
    intent_stats = (
        db.query(
            ChatMessage.Intent,
            func.count(ChatMessage.Intent).label('count')
        )
        .filter(
            ChatMessage.UserID == user_id,
            ChatMessage.CreatedAt >= cutoff_date,
            ChatMessage.Intent.isnot(None)
        )
        .group_by(ChatMessage.Intent)
        .order_by(desc('count'))
        .limit(10)
        .all()
    )
    
    most_common_intents = [
        {"intent": intent, "count": count}
        for intent, count in intent_stats
    ]
    
    # Actions performed
    action_stats = (
        db.query(
            ChatMessage.ActionTaken,
            func.count(ChatMessage.ActionTaken).label('count')
        )
        .filter(
            ChatMessage.UserID == user_id,
            ChatMessage.CreatedAt >= cutoff_date,
            ChatMessage.ActionTaken.isnot(None)
        )
        .group_by(ChatMessage.ActionTaken)
        .all()
    )
    
    actions_performed = {
        action: count for action, count in action_stats
    }
    
    return ChatAnalyticsResponse(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        total_messages=total_messages,
        average_messages_per_session=float(avg_messages),
        most_common_intents=most_common_intents,
        actions_performed=actions_performed,
        session_duration_stats={"avg": 0, "min": 0, "max": 0}  # Simplified for now
    )