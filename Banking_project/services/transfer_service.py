"""
services/transfer_service.py
-----------------------------
Handles fund transfers between accounts.
Uses atomic DB transactions to prevent partial transfers (money lost/duplicated).
"""

from sqlalchemy.orm import Session
from models import Account, Transaction, TransactionType, TransactionStatus
from utils.helpers import validate_amount, log_event, format_currency


def transfer_funds(
    db: Session,
    from_account_number: str,
    to_account_number: str,
    amount: float,
    description: str = "Fund Transfer"
) -> dict:
    """
    Transfers money from one account to another.
    
    Key safety:
    - Both accounts must exist and be active
    - Sender must have sufficient balance
    - Both debit + credit happen in ONE db.commit() → atomic
    - If anything fails, db.rollback() is called → no partial state
    
    Example:
        transfer_funds(db, "ACC111222333", "ACC444555666", 5000.0)
    """
    # ── Validation ─────────────────────────────────────────────────
    if from_account_number == to_account_number:
        return {"success": False, "message": "Cannot transfer to the same account."}

    if not validate_amount(amount):
        return {"success": False, "message": "Invalid transfer amount."}

    # Fetch accounts
    from_acc = db.query(Account).filter(Account.account_number == from_account_number).first()
    to_acc   = db.query(Account).filter(Account.account_number == to_account_number).first()

    if not from_acc:
        return {"success": False, "message": f"Source account {from_account_number} not found."}
    if not to_acc:
        return {"success": False, "message": f"Destination account {to_account_number} not found."}
    if not from_acc.is_active:
        return {"success": False, "message": "Source account is inactive."}
    if not to_acc.is_active:
        return {"success": False, "message": "Destination account is inactive."}
    if from_acc.balance < amount:
        return {
            "success": False,
            "message": f"Insufficient balance. Available: {format_currency(from_acc.balance)}"
        }

    # ── Execute Transfer ────────────────────────────────────────────
    try:
        # Debit sender
        from_acc.balance -= amount

        # Credit receiver
        to_acc.balance += amount

        # Record transaction (one entry in the sender's account)
        txn = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            status=TransactionStatus.COMPLETED,
            description=description,
            account_id=from_acc.id,
            target_account_id=to_acc.id
        )
        db.add(txn)
        db.commit()  # ← single atomic commit

        log_event(
            f"Transfer {format_currency(amount)} | {from_account_number} → {to_account_number}"
        )

        return {
            "success": True,
            "message": f"Transferred {format_currency(amount)} to {to_account_number}.",
            "sender_balance": from_acc.balance,
            "transaction_id": txn.id
        }

    except Exception as e:
        db.rollback()  # ← undo everything if something went wrong
        log_event(f"Transfer FAILED: {from_account_number} → {to_account_number} | Error: {str(e)}")
        return {"success": False, "message": f"Transfer failed: {str(e)}"}


def get_transfer_history(db: Session, account_number: str) -> dict:
    """
    Returns all TRANSFER-type transactions for an account
    (both sent and received transfers).
    """
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}

    transfers = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_type == TransactionType.TRANSFER,
            (Transaction.account_id == account.id) | (Transaction.target_account_id == account.id)
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )

    result = []
    for t in transfers:
        direction = "SENT" if t.account_id == account.id else "RECEIVED"
        result.append({
            "id": t.id,
            "direction": direction,
            "amount": t.amount,
            "formatted": format_currency(t.amount),
            "status": t.status.value,
            "date": str(t.created_at)
        })

    return {"success": True, "transfers": result}
