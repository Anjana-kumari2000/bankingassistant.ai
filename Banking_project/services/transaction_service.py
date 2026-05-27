"""
services/transaction_service.py
--------------------------------
Handles deposit, withdrawal, and transaction history logic.
"""

from sqlalchemy.orm import Session
from models import Account, Transaction, TransactionType, TransactionStatus
from utils.helpers import validate_amount, log_event, format_currency
from typing import List, Optional


def deposit(db: Session, account_number: str, amount: float, description: str = "Deposit") -> dict:
    """
    Adds money to an account.
    
    Steps:
    1. Find the account
    2. Validate amount
    3. Add amount to balance
    4. Record transaction
    """
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}
    if not account.is_active:
        return {"success": False, "message": "Account is inactive."}
    if not validate_amount(amount):
        return {"success": False, "message": "Invalid deposit amount."}

    # Update balance
    account.balance += amount

    # Record the transaction
    txn = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        description=description,
        account_id=account.id
    )
    db.add(txn)
    db.commit()

    log_event(f"Deposit {format_currency(amount)} → {account_number}")
    return {
        "success": True,
        "message": f"Deposited {format_currency(amount)} successfully.",
        "new_balance": account.balance
    }


def withdraw(db: Session, account_number: str, amount: float, description: str = "Withdrawal") -> dict:
    """
    Deducts money from an account if sufficient balance exists.
    """
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}
    if not account.is_active:
        return {"success": False, "message": "Account is inactive."}
    if not validate_amount(amount):
        return {"success": False, "message": "Invalid withdrawal amount."}
    if account.balance < amount:
        return {"success": False, "message": f"Insufficient balance. Available: {format_currency(account.balance)}"}

    account.balance -= amount

    txn = Transaction(
        transaction_type=TransactionType.WITHDRAWAL,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        description=description,
        account_id=account.id
    )
    db.add(txn)
    db.commit()

    log_event(f"Withdrawal {format_currency(amount)} ← {account_number}")
    return {
        "success": True,
        "message": f"Withdrawn {format_currency(amount)} successfully.",
        "new_balance": account.balance
    }


def get_balance(db: Session, account_number: str) -> dict:
    """Returns current balance of an account."""
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}
    return {
        "success": True,
        "account_number": account_number,
        "balance": account.balance,
        "formatted": format_currency(account.balance)
    }


def get_transaction_history(db: Session, account_number: str, limit: int = 10, offset: int = 0) -> dict:
    """
    Returns paginated list of transactions for an account.
    """
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}

    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "account_number": account_number,
        "transactions": [
            {
                "id": t.id,
                "type": t.transaction_type.value,
                "amount": t.amount,
                "formatted": format_currency(t.amount),
                "status": t.status.value,
                "description": t.description,
                "date": str(t.created_at)
            }
            for t in transactions
        ],
        "count": len(transactions)
    }
