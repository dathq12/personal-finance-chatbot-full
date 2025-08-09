# routers/transaction.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from database import get_db
from schemas.transaction_schema import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionResponse, 
    TransactionListResponse,
    TransactionFilter
)
from crud import transaction_crud as crud_transaction
from  crud.category_crud import get_category_display_name
from auth.auth_dependency import get_current_user  

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(HTTPBearer())]
)

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Create transaction
    created_transaction = crud_transaction.create_transaction(
        db=db,
        transaction_data=transaction,
        user_id=current_user.UserID,
    )
    
    return created_transaction

@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type: 'income' or 'expense'"),
    category_display_name: Optional[str] = Query(None, description="Filter by category display name"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    location: Optional[str] = Query(None, description="Filter by location"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    amount_min: Optional[float] = Query(None, description="Filter by minimum amount"),
    amount_max: Optional[float] = Query(None, description="Filter by maximum amount"),
    search: Optional[str] = Query(None, description="Search transactions by description or notes"),
    created_by: Optional[str] = Query(None, regex ="^(manual|chatbot)$", description="Filter by transaction creator: 'manual' or 'chatbot'"),

    skip: int = Query(0, ge=0, description="Number of transactions to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of transactions to return per page"),

    sort_by: Optional[str] = Query("created_at", description="Field to sort by, e.g., 'amount', 'transaction_date'"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order: 'asc' for ascending, 'desc' for descending"),

    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of transactions with optional filters, pagination, and sorting."""
    # Validate transaction type
    if transaction_type and transaction_type.lower() not in ['income', 'expense']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type. Must be 'income' or 'expense'.")

    # Validate created_by
    if created_by and created_by.lower() not in ['manual', 'chatbot']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid created_by value. Must be 'manual' or 'chatbot'.")

    # Get transactions with filters, pagination, and sorting
    filters = TransactionFilter(
        transaction_type=transaction_type,
        category_display_name=category_display_name,
        payment_method=payment_method,
        location= location,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
        search=search,
        created_by=created_by,
        skip=skip,
        limit=limit,
        order_by=sort_by,
        sort_order=sort_order
        )
    return crud_transaction.get_transactions(
        db=db,
        user_id=current_user.UserID,
        filters=filters
    )
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a single transaction by ID."""
    transaction = crud_transaction.get_transaction_by_id(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.UserID
    )
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    return transaction

