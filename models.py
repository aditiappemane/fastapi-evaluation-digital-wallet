"""Digital Wallet API Models Module"""

from sqlalchemy import Column, Integer, String, Float
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import datetime
import enum
from sqlalchemy import Enum



"""-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'CREDIT', 'DEBIT', 'TRANSFER_IN', 'TRANSFER_OUT'
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    reference_transaction_id INTEGER REFERENCES transactions(id), -- For linking transfer transactions
    recipient_user_id INTEGER REFERENCES users(id), -- For transfers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""

class TransactionType(enum.Enum):
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

class User(Base):
    __tablename__ = "users"     
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    phone_number = Column(String, nullable=True)
    balance = Column(Float, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())

    transactions = relationship("Transaction", back_populates="user", foreign_keys="Transaction.user_id")
    received_transactions = relationship("Transaction", back_populates="recipient", foreign_keys="Transaction.recipient_user_id")
    sent_transactions = relationship("Transaction", back_populates="sender", foreign_keys="Transaction.sender_user_id")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    reference_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    related_transaction = relationship("Transaction", remote_side=[id], uselist=False)

    user = relationship("User", back_populates="transactions", foreign_keys="Transaction.user_id")
    recipient = relationship("User", back_populates="received_transactions", foreign_keys="Transaction.recipient_user_id")
    sender = relationship("User", back_populates="sent_transactions", foreign_keys="Transaction.sender_user_id")
    reference = relationship("Transaction", remote_side=[id], uselist=False)

         



    