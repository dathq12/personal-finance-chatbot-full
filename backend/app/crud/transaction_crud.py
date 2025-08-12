from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, case
from uuid import UUID
from typing import List, Optional, Tuple
from datetime import datetime, date
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status

from models.transaction import Transaction
from models.category import Category,UserCategory
from schemas.transaction_schema import (
    TransactionCreate, 
    TransactionUpdate,
    TransactionResponse,
    TransactionFilter,
    TransactionListResponse)
from  crud.category_crud import get_category_display_name, get_user_category_id_by_display_name


def create_transaction(
    db: Session, 
    user_id: UUID, 
    transaction_data: TransactionCreate
) -> TransactionResponse:
    """Create a new transaction"""
    user_category_id = get_user_category_id_by_display_name(
        db= db, 
        user_id=user_id,
        display_name=transaction_data.category_display_name,
        transaction_type=transaction_data.transaction_type
    )
    if not user_category_id:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy danh mục phù hợp"
        )
    db_transaction = Transaction(
        UserID=user_id,
        UserCategoryID=user_category_id,
        TransactionType=transaction_data.transaction_type,
        Amount=transaction_data.amount,
        Description=transaction_data.description,
        TransactionDate=transaction_data.transaction_date,
        TransactionTime=transaction_data.transaction_time or datetime.now().time(),
        PaymentMethod=transaction_data.payment_method,
        Location=transaction_data.location,
        Notes=transaction_data.notes,
        CreatedBy= transaction_data.created_by
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Lấy tên hiển thị của danh mục
    category_display_name = get_category_display_name(db, user_category_id)
    
    # Chuyển đổi transaction object thành dict và thêm category_display_name
    transaction_dict = {
        'TransactionID': db_transaction.TransactionID,
        'UserID': db_transaction.UserID,
        'UserCategoryID': db_transaction.UserCategoryID,
        'transaction_type': db_transaction.TransactionType,
        'amount': db_transaction.Amount,
        'description': db_transaction.Description,
        'transaction_date': db_transaction.TransactionDate,
        'transaction_time': db_transaction.TransactionTime,
        'payment_method': db_transaction.PaymentMethod,
        'location': db_transaction.Location,
        'notes': db_transaction.Notes,
        'created_by': db_transaction.CreatedBy,
        'category_display_name': category_display_name,
        'CreatedAt': db_transaction.CreatedAt,
        'UpdatedAt': db_transaction.UpdatedAt
    }
    
    return TransactionResponse(**transaction_dict)

def get_transaction_by_id(
    db: Session, 
    user_id: UUID, 
    transaction_id: UUID
) -> TransactionResponse:
    """Get a transaction by ID"""
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.UserID == user_id,
            Transaction.TransactionID == transaction_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy giao dịch"
        )
    # Lấy tên hiển thị của danh mục
    category_display_name = get_category_display_name(db, transaction.UserCategoryID)
    
    # Chuyển đổi transaction object thành dict và thêm category_display_name
    transaction_dict = {
        'TransactionID': transaction.TransactionID,
        'UserID': transaction.UserID,
        'UserCategoryID': transaction.UserCategoryID,
        'transaction_type': transaction.TransactionType,
        'amount': transaction.Amount,
        'description': transaction.Description,
        'transaction_date': transaction.TransactionDate,
        'transaction_time': transaction.TransactionTime,
        'payment_method': transaction.PaymentMethod,
        'location': transaction.Location,
        'notes': transaction.Notes,
        'created_by': transaction.CreatedBy,
        'category_display_name': category_display_name,
        'CreatedAt': transaction.CreatedAt,
        'UpdatedAt': transaction.UpdatedAt
    }
    
    return TransactionResponse(**transaction_dict)

def get_transaction_by_id(
    db: Session,
    transaction_id: UUID,
    user_id: UUID) ->Optional[TransactionResponse]:
    """Get a transaction by ID"""
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.TransactionID == transaction_id,
            Transaction.UserID == user_id
        )
        .first()
    )
    if not transaction:
        return None
    # Lấy tên hiển thị của danh mục
    category_display_name = get_category_display_name(db, transaction.UserCategoryID)
    # Chuyển đổi transaction object thành dict và thêm category_display_name
    transaction_dict = {
        'TransactionID': transaction.TransactionID,
        'UserID': transaction.UserID,
        'UserCategoryID': transaction.UserCategoryID,
        'transaction_type': transaction.TransactionType,
        'amount': transaction.Amount,
        'description': transaction.Description,
        'transaction_date': transaction.TransactionDate,
        'transaction_time': transaction.TransactionTime,
        'payment_method': transaction.PaymentMethod,
        'location': transaction.Location,
        'notes': transaction.Notes,
        'created_by': transaction.CreatedBy,
        'category_display_name': category_display_name,
        'CreatedAt': transaction.CreatedAt,
        'UpdatedAt': transaction.UpdatedAt
    }
    return TransactionResponse(**transaction_dict)

def get_transactions(
    db: Session, 
    user_id: UUID, 
    filters: TransactionFilter
) -> TransactionListResponse:
    """Get transactions with optional filters"""
    # Build base query
    query = (
        db.query(Transaction, UserCategory, Category)
        .join(UserCategory, Transaction.UserCategoryID == UserCategory.UserCategoryID)
        .join(Category, UserCategory.CategoryID == Category.CategoryID)
        .filter(Transaction.UserID == user_id)
    )
    # Apply filters
    if filters.transaction_type:
        query = query.filter(Transaction.TransactionType == filters.transaction_type)
    
    if filters.category_display_name:
        query = query.filter(
            or_(
                UserCategory.CustomName == filters.category_display_name,
                and_(
                    UserCategory.CustomName.is_(None),
                    Category.CategoryName == filters.category_display_name
                )
            )
        )
    if filters.payment_method:
        query = query.filter(Transaction.PaymentMethod.ilike(f"%{filters.payment_method}%"))
    
    if filters.location:
        query = query.filter(Transaction.Location.ilike(f"%{filters.location}%"))
    
    if filters.date_from:
        query = query.filter(Transaction.TransactionDate >= filters.date_from)
    if filters.date_to:
        query = query.filter(Transaction.TransactionDate <= filters.date_to)
    
    if filters.amount_min:
        query = query.filter(Transaction.Amount >= filters.amount_min)
    if filters.amount_max:
        query = query.filter(Transaction.Amount <= filters.amount_max)
    
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Transaction.Description.ilike(search_term),
                Transaction.Notes.ilike(search_term)
            )
        )
    if filters.created_by:
        query = query.filter(Transaction.CreatedBy == filters.created_by)

    # Đếm tổng số lượng giao dịch
    total_count = query.count()

    total_query = query.with_entities(
        func.sum(case((Transaction.TransactionType == 'income', Transaction.Amount), else_=0)).label('total_income'),
        func.sum(case((Transaction.TransactionType == 'expense', Transaction.Amount), else_=0)).label('total_expense')
    ).first()

    total_income = total_query.total_income if total_query.total_income else 0
    total_expense = total_query.total_expense if total_query.total_expense else 0
    net_amount = total_income - total_expense

    # Apply sorting - Updated to use sort_by instead of order_by
    sort_field = getattr(Transaction, filters.sort_by, Transaction.TransactionDate)
    if filters.sort_order == 'desc':
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))

    # Apply pagination
    query = query.offset(filters.skip).limit(filters.limit)

    # Execute query and get results
    results = query.all()

    transactions = []
    for transaction, user_category, category in results:
        category_display_name = user_category.CustomName if user_category.CustomName else category.CategoryName
        
        # Chuyển đổi transaction object thành dict và thêm category_display_name
        transaction_dict = {
            'TransactionID': transaction.TransactionID,
            'UserID': transaction.UserID,
            'UserCategoryID': transaction.UserCategoryID,
            'transaction_type': transaction.TransactionType,
            'amount': transaction.Amount,
            'description': transaction.Description,
            'transaction_date': transaction.TransactionDate,
            'transaction_time': transaction.TransactionTime,
            'payment_method': transaction.PaymentMethod,
            'location': transaction.Location,
            'notes': transaction.Notes,
            'created_by': transaction.CreatedBy,
            'category_display_name': category_display_name,
            'CreatedAt': transaction.CreatedAt,
            'UpdatedAt': transaction.UpdatedAt
        }
        
        transactions.append(TransactionResponse(**transaction_dict))

    return TransactionListResponse(
        transaction=transactions,  
        total_count=total_count,
        total_income=total_income,
        total_expense=total_expense,
        net_amount=net_amount
    )

def update_transaction(
    db: Session, 
    user_id: UUID, 
    transaction_id: UUID, 
    transaction_data: TransactionUpdate
) -> TransactionResponse:
    """Update an existing transaction"""
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.UserID == user_id,
            Transaction.TransactionID == transaction_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy giao dịch"
        )

    # Cập nhật danh mục nếu cần
    if transaction_data.category_display_name:
        user_category_id = get_user_category_id_by_display_name(
            db=db, 
            user_id=user_id,
            display_name=transaction_data.category_display_name,
            transaction_type=transaction.TransactionType
        )
        if not user_category_id:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy danh mục phù hợp"
            )
        transaction.UserCategoryID = user_category_id

    # Cập nhật các trường giao dịch (trừ category_display_name)
    update_data = transaction_data.model_dump(exclude_unset=True, exclude={'category_display_name'})
    for key, value in update_data.items():
        if key == 'transaction_type':
            setattr(transaction, 'TransactionType', value)
        elif key == 'payment_method':
            setattr(transaction, 'PaymentMethod', value)
        elif key == 'transaction_date':
            setattr(transaction, 'TransactionDate', value)
        elif key == 'transaction_time':
            setattr(transaction, 'TransactionTime', value)
        elif key == 'created_by':
            setattr(transaction, 'CreatedBy', value)
        else:
            # Capitalize first letter for other fields
            field_name = key.capitalize()
            setattr(transaction, field_name, value)

    db.commit()
    db.refresh(transaction)

    # Lấy tên hiển thị của danh mục
    category_display_name = get_category_display_name(db, transaction.UserCategoryID)
    
    # Chuyển đổi transaction object thành dict và thêm category_display_name
    transaction_dict = {
        'TransactionID': transaction.TransactionID,
        'UserID': transaction.UserID,
        'UserCategoryID': transaction.UserCategoryID,
        'transaction_type': transaction.TransactionType,
        'amount': transaction.Amount,
        'description': transaction.Description,
        'transaction_date': transaction.TransactionDate,
        'transaction_time': transaction.TransactionTime,
        'payment_method': transaction.PaymentMethod,
        'location': transaction.Location,
        'notes': transaction.Notes,
        'created_by': transaction.CreatedBy,
        'category_display_name': category_display_name,
        'CreatedAt': transaction.CreatedAt,
        'UpdatedAt': transaction.UpdatedAt
    }
    
    return TransactionResponse(**transaction_dict)

def delete_transaction(db: Session, transaction_id: UUID, user_id: UUID) -> bool:
    """Delete a transaction"""
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.TransactionID == transaction_id,
            Transaction.UserID == user_id
        )
        .first()
    )
    
    if not transaction:
        return False
    
    db.delete(transaction)
    db.commit()
    return True

def get_transaction_summary(
    db: Session, 
    user_id: UUID, 
    date_from: Optional[date] = None, 
    date_to: Optional[date] = None
) -> dict:
    """Get transaction summary for a user"""
    query = db.query(
        func.sum(case((Transaction.TransactionType == 'income', Transaction.Amount), else_=0)).label('total_income'),
        func.sum(case((Transaction.TransactionType == 'expense', Transaction.Amount), else_=0)).label('total_expense')
    ).filter(Transaction.UserID == user_id)

    if date_from:
        query = query.filter(Transaction.TransactionDate >= date_from)
    if date_to:
        query = query.filter(Transaction.TransactionDate <= date_to)

    result = query.first()

    # Nếu không có kết quả hoặc tất cả đều None
    if not result or (result.total_income is None and result.total_expense is None):
        return {
            "message": "Không có giao dịch trong khoảng thời gian này",
            "total_income": 0,
            "total_expense": 0,
            "net_amount": 0
        }

    total_income = result.total_income or 0
    total_expense = result.total_expense or 0

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_amount': total_income - total_expense
    }
