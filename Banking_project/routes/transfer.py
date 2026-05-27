"""
routes/transfer.py
------------------
API endpoints for fund transfers between accounts.
Prefix: /transfer
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services import transfer_service
from routes.user import get_current_user_from_token

router = APIRouter(prefix="/transfer", tags=["Transfer"])


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
    description: str = "Fund Transfer"


@router.post("/send")
def send_transfer(
    data: TransferRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    POST /transfer/send
    Transfer money between two accounts atomically.
    
    Body: { "from_account": "ACC...", "to_account": "ACC...", "amount": 1000 }
    """
    result = transfer_service.transfer_funds(
        db, data.from_account, data.to_account, data.amount, data.description
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/history/{account_number}")
def transfer_history(
    account_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_token)
):
    """
    GET /transfer/history/{account_number}
    Returns all transfers (sent and received) for an account.
    """
    result = transfer_service.get_transfer_history(db, account_number)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result
