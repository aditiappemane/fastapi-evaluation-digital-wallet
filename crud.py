"""Digital Wallet Crud operations Module"""

from sqlalchemy.orm import Session
from models import User, Transaction, TransactionType
import schemas,models
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from database import get_db
from typing import List, Optional
from datetime import datetime

"""User CRUD Operations"""

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        balance=user.initial_balance if user.initial_balance else 0.0,
        hashed_password=user.password,  # Note: In a real app, you should hash the password
        created_at=datetime.utcnow()
          
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for var, value in vars(user_update).items():
        if value is not None:
            setattr(db_user, var, value)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


"""wallet balance operations"""

""""get balance of user"""

def get_user_balance(db: Session, user_id: int) -> Optional[float]:
    db_user = get_user(db, user_id) 
    if db_user:
        return db_user.balance
    return None




"""update balance of user"""
def update_user_balance(db: Session, user_id: int, new_balance: float) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.balance = new_balance
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def add_money(db: Session, user_id: int, amount: float, description: Optional[str] = None) -> Optional[Transaction]:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_balance = db_user.balance + amount
    db_user.balance = new_balance
    db_user.updated_at = datetime.utcnow()
    db_transaction = Transaction(
        user_id=user_id,
        transaction_type=TransactionType.CREDIT,
        amount=amount,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction



def withdraw_money(db: Session, user_id: int, amount: float, description: Optional[str] = None) -> Optional[Transaction]:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")  
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    new_balance = db_user.balance - amount
    db_user.balance = new_balance
    db_user.updated_at = datetime.utcnow()
    db_transaction = Transaction(
        user_id=user_id,
        transaction_type=TransactionType.DEBIT,
        amount=amount,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


"""Transaction CRUD Operations"""


def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int) -> Transaction:
    db_transaction = Transaction(
        user_id=transaction.user_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        reference_transaction_id=transaction.reference_transaction_id,
        recipient_user_id=transaction.recipient_user_id,
        sender_user_id=transaction.sender_user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_transactions(db: Session, user_id: int, page: int = 1, limit: int = 10) -> List[Transaction]:
    offset = (page - 1) * limit
    return db.query(Transaction).filter(Transaction.user_id == user_id).offset(offset).limit(limit).all()
def get_transactions_by_type(db: Session, user_id: int, transaction_type: TransactionType, page: int = 1, limit: int = 10) -> List[Transaction]:
    offset = (page - 1) * limit
    return db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type
        )
    ).offset(offset).limit(limit).all()


"Transfer money between users"

def transfer_money(db: Session, sender_id: int, recipient_id: int, amount: float, description: Optional[str] = None) -> Optional[Transaction]:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    if sender_id == recipient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to self")
    sender = get_user(db, sender_id)
    recipient = get_user(db, recipient_id)
    if not sender or not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if sender.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    sender.balance -= amount
    recipient.balance += amount
    sender.updated_at = datetime.utcnow()
    recipient.updated_at = datetime.utcnow()
    transfer_out = Transaction(
        user_id=sender_id,
        transaction_type=TransactionType.TRANSFER_OUT,
        amount=amount,
        description=description or f"Transfer to user {recipient_id}",
        recipient_user_id=recipient_id,
        created_at=datetime.utcnow()
    )
    
    transfer_in = Transaction(
        user_id=recipient_id,
        transaction_type=TransactionType.TRANSFER_IN,
        amount=amount,
        description=description or f"Transfer from user {sender_id}",
        recipient_user_id=recipient_id,
        sender_user_id=sender_id,
        created_at=datetime.utcnow()
    )
    db.add(transfer_out)
    db.add(transfer_in)
    db.commit()
    db.refresh(transfer_out)
    return transfer_out


"create end point tranfer moeny with transfer id"

def transfer_money_with_reference(db: Session, sender_id: int, recipient_id: int, amount: float, reference_transaction_id: int, description: Optional[str] = None) -> Optional[Transaction]:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    if sender_id == recipient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to self")
    sender = get_user(db, sender_id)
    recipient = get_user(db, recipient_id)
    if not sender or not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if sender.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    reference_transaction = get_transaction(db, reference_transaction_id)
    if not reference_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference transaction not found")
    sender.balance -= amount
    recipient.balance += amount
    sender.updated_at = datetime.utcnow()
    recipient.updated_at = datetime.utcnow()
    transfer_out = Transaction(
        user_id=sender_id,
        transaction_type=TransactionType.TRANSFER_OUT,
        amount=amount,
        description=description or f"Transfer to user {recipient_id}",
        recipient_user_id=recipient_id,
        reference_transaction_id=reference_transaction_id,
        created_at=datetime.utcnow()
    )
    transfer_in = Transaction(
        user_id=recipient_id,
        transaction_type=TransactionType.TRANSFER_IN,
        amount=amount,
        description=description or f"Transfer from user {sender_id}",
        recipient_user_id=recipient_id,
        sender_user_id=sender_id,
        reference_transaction_id=reference_transaction_id,
        created_at=datetime.utcnow()
    )
    db.add(transfer_out)
    db.add(transfer_in)
    db.commit()
    db.refresh(transfer_out)
    return transfer_out






