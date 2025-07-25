from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from models.transaction import Transaction
from schemas.transaction_schema import TransactionCreate, TransactionUpdate, TransactionFilter
from uuid import UUID
from typing import List, Optional, Tuple
from datetime import datetime, date
import json

class TransactionCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.db.query(Transaction).filter(
            Transaction.TransactionID == transaction_id
        ).first()

    def get_by_user(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "transaction_date",
        order_dir: str = "desc"
    ) -> List[Transaction]:
        """Get transactions by user with pagination and sorting"""
        query = self.db.query(Transaction).filter(Transaction.UserID == user_id)
        
        # Apply ordering
        if order_dir.lower() == "desc":
            if order_by == "amount":
                query = query.order_by(desc(Transaction.Amount))
            elif order_by == "created_at":
                query = query.order_by(desc(Transaction.CreatedAt))
            else:  # default to transaction_date
                query = query.order_by(desc(Transaction.TransactionDate))
        else:
            if order_by == "amount":
                query = query.order_by(asc(Transaction.Amount))
            elif order_by == "created_at":
                query = query.order_by(asc(Transaction.CreatedAt))
            else:  # default to transaction_date
                query = query.order_by(asc(Transaction.TransactionDate))
        
        return query.offset(skip).limit(limit).all()

    def get_filtered(
        self, 
        user_id: UUID, 
        filters: TransactionFilter,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Transaction], int]:
        """Get filtered transactions with count"""
        query = self.db.query(Transaction).filter(Transaction.UserID == user_id)
        
        # Apply filters
        if filters.category_id:
            query = query.filter(Transaction.CategoryID == filters.category_id)
        
        if filters.transaction_type:
            query = query.filter(Transaction.TransactionType == filters.transaction_type)
        
        if filters.start_date:
            query = query.filter(Transaction.TransactionDate >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Transaction.TransactionDate <= filters.end_date)
        
        if filters.min_amount:
            query = query.filter(Transaction.Amount >= filters.min_amount)
        
        if filters.max_amount:
            query = query.filter(Transaction.Amount <= filters.max_amount)
        
        if filters.payment_method:
            query = query.filter(Transaction.PaymentMethod == filters.payment_method)
        
        if filters.is_recurring is not None:
            query = query.filter(Transaction.IsRecurring == filters.is_recurring)
        
        if filters.tags:
            # Search for any of the provided tags
            tag_conditions = []
            for tag in filters.tags:
                tag_conditions.append(Transaction.Tags.like(f'%"{tag}"%'))
            query = query.filter(or_(*tag_conditions))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        transactions = query.order_by(desc(Transaction.TransactionDate)).offset(skip).limit(limit).all()
        
        return transactions, total

    def create(self, user_id: UUID, transaction_data: TransactionCreate) -> Transaction:
        """Create new transaction"""
        # Convert tags list to JSON string if provided
        transaction_dict = transaction_data.dict()
        if transaction_dict.get('tags'):
            transaction_dict['tags'] = json.dumps(transaction_dict['tags'])
        
        # Map schema fields to model fields
        db_transaction = Transaction(
            UserID=user_id,
            CategoryID=transaction_dict['category_id'],
            TransactionType=transaction_dict['transaction_type'],
            Amount=transaction_dict['amount'],
            Description=transaction_dict.get('description'),
            TransactionDate=transaction_dict['transaction_date'],
            TransactionTime=transaction_dict.get('transaction_time'),
            PaymentMethod=transaction_dict.get('payment_method'),
            Location=transaction_dict.get('location'),
            Tags=transaction_dict.get('tags'),
            ReceiptURL=transaction_dict.get('receipt_url'),
            Notes=transaction_dict.get('notes'),
            IsRecurring=transaction_dict.get('is_recurring', False),
            RecurringPattern=transaction_dict.get('recurring_pattern'),
            CreatedBy=transaction_dict.get('created_by', 'manual')
        )
        
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def update(self, transaction_id: UUID, user_id: UUID, updates: TransactionUpdate) -> Optional[Transaction]:
        """Update transaction"""
        db_transaction = self.db.query(Transaction).filter(
            and_(
                Transaction.TransactionID == transaction_id,
                Transaction.UserID == user_id
            )
        ).first()
        
        if not db_transaction:
            return None
        
        update_dict = updates.dict(exclude_unset=True)
        
        # Convert tags list to JSON string if provided
        if 'tags' in update_dict and update_dict['tags']:
            update_dict['tags'] = json.dumps(update_dict['tags'])
        
        # Map schema fields to model fields
        field_mapping = {
            'category_id': 'CategoryID',
            'transaction_type': 'TransactionType',
            'amount': 'Amount',
            'description': 'Description',
            'transaction_date': 'TransactionDate',
            'transaction_time': 'TransactionTime',
            'payment_method': 'PaymentMethod',
            'location': 'Location',
            'tags': 'Tags',
            'receipt_url': 'ReceiptURL',
            'notes': 'Notes',
            'is_recurring': 'IsRecurring',
            'recurring_pattern': 'RecurringPattern'
        }
        
        for schema_field, model_field in field_mapping.items():
            if schema_field in update_dict:
                setattr(db_transaction, model_field, update_dict[schema_field])
        
        db_transaction.UpdatedAt = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def delete(self, transaction_id: UUID, user_id: UUID) -> bool:
        """Delete transaction"""
        db_transaction = self.db.query(Transaction).filter(
            and_(
                Transaction.TransactionID == transaction_id,
                Transaction.UserID == user_id
            )
        ).first()
        
        if not db_transaction:
            return False
        
        self.db.delete(db_transaction)
        self.db.commit()
        return True

    def get_summary(self, user_id: UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        """Get transaction summary for user"""
        query = self.db.query(Transaction).filter(Transaction.UserID == user_id)
        
        if start_date:
            query = query.filter(Transaction.TransactionDate >= start_date)
        if end_date:
            query = query.filter(Transaction.TransactionDate <= end_date)
        
        transactions = query.all()
        
        total_income = sum(t.Amount for t in transactions if t.TransactionType == 'income')
        total_expense = sum(t.Amount for t in transactions if t.TransactionType == 'expense')
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense,
            'transaction_count': len(transactions)
        }

    def get_by_category(self, user_id: UUID, category_id: UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions by category"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.UserID == user_id,
                    Transaction.CategoryID == category_id
                )
            )
            .order_by(desc(Transaction.TransactionDate))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recurring(self, user_id: UUID) -> List[Transaction]:
        """Get recurring transactions"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.UserID == user_id,
                    Transaction.IsRecurring == True
                )
            )
            .order_by(desc(Transaction.TransactionDate))
            .all()
        )
    
    #Cập nhật save_chat_message (25/7/25 Sơn)
    def save_chat_message(db: Session, user_id: str, session_id: str, question: str, answer: str, intent: str = None, entities: dict = None, confidence_score: float = None):
    chat_message = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        message_type="user" if question else "bot",
        content=question if question else answer,
        intent=intent,
        entities=entities,
        confidence_score=confidence_score,
        action_taken="recorded" if intent == "record_transaction" else None
    )
    db.add(chat_message)
    db.commit()
    # Cập nhật MessageCount trong ChatSession
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.message_count += 1
        db.commit()
    return chat_message