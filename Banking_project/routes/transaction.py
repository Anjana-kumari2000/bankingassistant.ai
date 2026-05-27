"""
routes/transaction.py
----------------------
API endpoints for deposits, withdrawals, balance check, history.
Prefix: /transaction
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services import transaction_service
from routes.user import get_current_user_from_token

router = APIRouter(prefix="/transaction", tags=["Transaction"])


class DepositRequest(BaseModel):
    account_number: str
    amount: float
    description: str = "Deposit"


class WithdrawRequest(BaseModel):
    account_number: str
    amount: float
    description: str = "Withdrawal"


@router.post("/deposit")
def deposit(
    data: DepositRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    POST /transaction/deposit
    Deposit money into an account.
    """
    result = transaction_service.deposit(db, data.account_number, data.amount, data.description)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/withdraw")
def withdraw(
    data: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    POST /transaction/withdraw
    Withdraw money from an account (checks balance first).
    """
    result = transaction_service.withdraw(db, data.account_number, data.amount, data.description)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/balance/{account_number}")
def get_balance(
    account_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    GET /transaction/balance/{account_number}
    Returns current balance for given account.
    """
    result = transaction_service.get_balance(db, account_number)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.get("/history/{account_number}")
def get_history(
    account_number: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    GET /transaction/history/{account_number}?limit=10&offset=0
    Returns paginated transaction history.
    """
    result = transaction_service.get_transaction_history(db, account_number, limit, offset)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result
