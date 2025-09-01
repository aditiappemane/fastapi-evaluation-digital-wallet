"""Digital Wallet API Schemas Module"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import enum 

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"   
    REFUND = "REFUND"
    PAYMENT = "PAYMENT"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    FEE = "FEE"
    ADJUSTMENT = "ADJUSTMENT"
    REVERSAL = "REVERSAL"
    CHARGEBACK = "CHARGEBACK"


"""User Schemas"""

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None 

class UserCreate(UserBase):
    password: str   
    initial_balance: Optional[float] = 0.0

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    balance: Optional[float] = None

class User(UserBase):
    id: int
    hashed_password: str
    is_active: int
    balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

"""Transaction Schemas"""

class TransactionBase(BaseModel):
    transaction_type: TransactionType
    amount: float
    description: Optional[str] = None
    reference_transaction_id: Optional[int] = None
    recipient_user_id: Optional[int] = None 
    sender_user_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    user_id: int

class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True