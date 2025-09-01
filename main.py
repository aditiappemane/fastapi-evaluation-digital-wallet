from fastapi import FastAPI
from database import Base, engine
import models,schemas,crud
from sqlalchemy.orm import Session
from database import get_db
from fastapi import Depends
from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime




# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Wallet API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Digital Wallet API"}



"create_user for user registration"
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

"get user by id"

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

"update user details"

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

"get userID balance details"

@app.get("/wallet/{user_id}/balance")
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = crud.get_user_balance(db, user_id=user_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "balance": balance}


"add money to wallet"

@app.post("/wallet/{user_id}/add")
def add_money(user_id: int, amount: float, description: Optional[str] = None, db: Session = Depends(get_db)):
    transaction = crud.add_money(db, user_id=user_id, amount=amount, description=description)
    return {"message": "Money added successfully", "transaction": transaction}

"withdraw money from wallet"

@app.post("/wallet/{user_id}/withdraw")
def withdraw_money(user_id: int, amount: float, description: Optional[str] = None, db: Session = Depends(get_db)):
    transaction = crud.withdraw_money(db, user_id=user_id, amount=amount, description=description)
    return {"message": "Money withdrawn successfully", "transaction": transaction}

"get the transaction of the user by userID using pagination"

@app.get("/transactions/{user_id}", response_model=List[schemas.Transaction]) 
def get_transactions(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, user_id=user_id, skip=skip, limit=limit)
    return transactions 


"Get transaction by transaction ID"

@app.get("/transaction/{transaction_id}", response_model=schemas.Transaction)   
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")  
    return db_transaction

"Create a transaction (for transfers, payments, etc.)"

@app.post("/transactions/", response_model=schemas.Transaction) 
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if not crud.get_user(db, user_id=transaction.user_id):
        raise HTTPException(status_code=404, detail="User not found")   
    db_transaction = crud.create_transaction(db, transaction=transaction, user_id=transaction.user_id)
    return db_transaction

"transfer money between users"

"POST /transfer"
@app.post("/transfer/")
def transfer_money(sender_id: int, recipient_id: int, amount: float, description: Optional[str] = None, db: Session = Depends(get_db)):
    transaction = crud.transfer_money(db, sender_id=sender_id, recipient_id=recipient_id, amount=amount, description=description)
    if transaction is None:
        raise HTTPException(status_code=400, detail="Transfer failed")
    return {"message": "Transfer successful", "transaction": transaction}

@app.get("/transfer/{transfer_id}", response_model=schemas.Transaction)
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id=transfer_id)
    if transaction is None or transaction.transaction_type not in [schemas.TransactionType.TRANSFER_IN, schemas.TransactionType.TRANSFER_OUT]:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transaction