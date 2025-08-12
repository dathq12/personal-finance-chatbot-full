# routers/chatbot.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database import get_db
from schemas.chat_schema import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionFilter,
    ChatSessionListResponse,
    ChatInteractionRequest,
    ChatInteractionResponse,
    ChatConversationResponse,
    ChatAnalyticsResponse,
    MessageType,
    Intent,
    ActionType
)
from crud import chatbot_crud
from services.gpt_service import chatbot_service
from auth.auth_dependency import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["chatbot"],
    dependencies=[Depends(HTTPBearer())]
)

# Chat Session Endpoints (unchanged)
@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat session"""
    return chatbot_crud.create_chat_session(
        db=db,
        user_id=current_user.UserID,
        session_data=session_data
    )

@router.get("/sessions", response_model=ChatSessionListResponse)
def get_chat_sessions(
    is_active: Optional[bool] = Query(None, description="Filter by active sessions"),
    session_name: Optional[str] = Query(None, description="Search by session name"),
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    sort_by: Optional[str] = Query("started_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat sessions with filters"""
    filters = ChatSessionFilter(
        is_active=is_active,
        session_name=session_name,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return chatbot_crud.get_chat_sessions(
        db=db,
        user_id=current_user.UserID,
        filters=filters
    )

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific chat session"""
    session = chatbot_crud.get_chat_session_by_id(
        db=db,
        user_id=current_user.UserID,
        session_id=session_id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: UUID,
    session_data: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a chat session"""
    session = chatbot_crud.update_chat_session(
        db=db,
        user_id=current_user.UserID,
        session_id=session_id,
        session_data=session_data
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
def end_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """End a chat session"""
    session = chatbot_crud.end_chat_session(
        db=db,
        user_id=current_user.UserID,
        session_id=session_id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
def delete_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a chat session and all its messages"""
    success = chatbot_crud.delete_chat_session(
        db=db,
        user_id=current_user.UserID,
        session_id=session_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return {"detail": "Chat session deleted successfully"}

# Conversation Endpoints
@router.get("/sessions/{session_id}/conversation", response_model=ChatConversationResponse)
def get_conversation(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get full conversation (session + messages)"""
    conversation = chatbot_crud.get_conversation(
        db=db,
        session_id=session_id,
        user_id=current_user.UserID
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return conversation

# Main Chat Interaction Endpoint - UPDATED WITH ASYNC
@router.post("/interact", response_model=ChatInteractionResponse)
async def chat_interact(
    interaction: ChatInteractionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Main chat interaction endpoint with AI integration"""
    try:
        # Get or create session
        if interaction.session_id:
            session = chatbot_crud.get_chat_session_by_id(
                db=db,
                user_id=current_user.UserID,
                session_id=interaction.session_id
            )
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            # Create new session
            session_data = ChatSessionCreate(
                session_name=interaction.session_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            session = chatbot_crud.create_chat_session(
                db=db,
                user_id=current_user.UserID,
                session_data=session_data
            )
        
        # Process user message with AI
        intent, confidence = chatbot_service.detect_intent(interaction.message)
        entities = chatbot_service.extract_entities(interaction.message, intent)
        
        # Save user message
        user_message = chatbot_crud.create_chat_message(
            db=db,
            session_id=session.SessionID,
            user_id=current_user.UserID,
            message_type=MessageType.USER,
            content=interaction.message,
            intent=intent,
            entities=entities,
            confidence_score=confidence
        )
        
        # Generate bot response with AI - NOW ASYNC
        bot_response_text, action_taken, action_data = await chatbot_service.generate_response(
            intent=intent,
            entities=entities,
            user_id=current_user.UserID,
            user_message=interaction.message,  # Pass original message for AI context
            db=db
        )
        
        # Save bot response
        bot_message = chatbot_crud.create_chat_message(
            db=db,
            session_id=session.SessionID,
            user_id=current_user.UserID,
            message_type=MessageType.BOT,
            content=bot_response_text,
            action_taken=action_taken
        )
        
        # Get updated session info
        updated_session = chatbot_crud.get_chat_session_by_id(
            db=db,
            user_id=current_user.UserID,
            session_id=session.SessionID
        )
        
        return ChatInteractionResponse(
            session_id=session.SessionID,
            user_message=user_message,
            bot_response=bot_message,
            session_info=updated_session,
            action_performed=action_data
        )
        
    except Exception as e:
        # Log error and return fallback response
        print(f"Chat interaction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chat message. Please try again."
        )

# Quick Chat Endpoint - UPDATED WITH ASYNC
@router.post("/quick", response_model=dict)
async def quick_chat(
    message: str = Query(..., min_length=1, max_length=500, description="Quick message"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Quick chat without session management - with AI integration"""
    try:
        # Process message
        intent, confidence = chatbot_service.detect_intent(message)
        entities = chatbot_service.extract_entities(message, intent)
        
        # Generate response with AI
        response_text, action_taken, action_data = await chatbot_service.generate_response(
            intent=intent,
            entities=entities,
            user_id=current_user.UserID,
            user_message=message,
            db=db
        )
        
        return {
            "user_message": message,
            "bot_response": response_text,
            "intent": intent.value,
            "confidence": confidence,
            "entities": entities,
            "action_taken": action_taken.value if action_taken else None,
            "action_data": action_data
        }
        
    except Exception as e:
        return {
            "user_message": message,
            "bot_response": "Xin lỗi, tôi không thể xử lý yêu cầu này lúc này. Vui lòng thử lại sau.",
            "error": str(e)
        }

# Analytics Endpoint
@router.get("/analytics", response_model=ChatAnalyticsResponse)
def get_chat_analytics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get chat analytics for the user"""
    return chatbot_crud.get_chat_analytics(
        db=db,
        user_id=current_user.UserID,
        days_back=days_back
    )

# Health Check
@router.get("/health")
def chat_health_check():
    """Health check for chatbot service"""
    return {
        "status": "healthy",
        "service": "financial_chatbot",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "intent_detection",
            "entity_extraction", 
            "transaction_creation",
            "financial_advice",
            "balance_inquiry",
            "ai_powered_responses"
        ]
    }

# Test AI Connection Endpoint
@router.get("/test-ai")
async def test_ai_connection():
    """Test AI connection and capabilities"""
    try:
        test_response = await chatbot_service.generate_ai_response(
            user_message="Hello, test message",
            intent=Intent.GENERAL_QUERY,
            entities={}
        )
        
        return {
            "status": "success",
            "ai_connection": "working",
            "test_response": test_response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "ai_connection": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }