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
    TransactionSummary,
    TransactionFilter
)
from crud.transaction_crud import TransactionCRUD
from auth.auth_dependency import get_current_user  

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(HTTPBearer())]
)

# Helper function to get transaction CRUD
def get_transaction_crud(db: Session = Depends(get_db)) -> TransactionCRUD:
    return TransactionCRUD(db)

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Create a new transaction"""
    try:
        db_transaction = transaction_crud.create(current_user.id, transaction)
        return db_transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create transaction: {str(e)}"
        )

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions to return"),
    order_by: str = Query("transaction_date", description="Field to order by"),
    order_dir: str = Query("desc", regex="^(asc|desc)$", description="Order direction"),
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Get user's transactions with pagination and sorting"""
    transactions = transaction_crud.get_by_user(
        current_user.id, 
        skip=skip, 
        limit=limit,
        order_by=order_by,
        order_dir=order_dir
    )
    return transactions

@router.get("/search", response_model=dict)
async def search_transactions(
    category_id: Optional[UUID] = Query(None),
    transaction_type: Optional[str] = Query(None, regex="^(income|expense)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    payment_method: Optional[str] = Query(None),
    is_recurring: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Search and filter transactions"""
    filters = TransactionFilter(
        category_id=category_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        payment_method=payment_method,
        is_recurring=is_recurring
    )
    
    transactions, total = transaction_crud.get_filtered(
        current_user.id, 
        filters, 
        skip=skip, 
        limit=limit
    )
    
    return {
        "transactions": transactions,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }

@router.get("/summary", response_model=TransactionSummary)
async def get_transaction_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Get transaction summary for user"""
    summary = transaction_crud.get_summary(current_user.id, start_date, end_date)
    return summary

@router.get("/recurring", response_model=List[TransactionResponse])
async def get_recurring_transactions(
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Get all recurring transactions"""
    transactions = transaction_crud.get_recurring(current_user.id)
    return transactions

@router.get("/category/{category_id}", response_model=List[TransactionResponse])
async def get_transactions_by_category(
    category_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Get transactions by category"""
    transactions = transaction_crud.get_by_category(
        current_user.id, 
        category_id, 
        skip=skip, 
        limit=limit
    )
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Get specific transaction"""
    transaction = transaction_crud.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Check if transaction belongs to current user
    if transaction.UserID != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transaction"
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    updates: TransactionUpdate,
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Update transaction"""
    transaction = transaction_crud.update(transaction_id, current_user.id, updates)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or not authorized"
        )
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user = Depends(get_current_user),
    transaction_crud: TransactionCRUD = Depends(get_transaction_crud)
):
    """Delete transaction"""
    success = transaction_crud.delete(transaction_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or not authorized"
        )
    return None