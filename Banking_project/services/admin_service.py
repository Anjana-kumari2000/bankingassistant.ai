"""
services/admin_service.py
--------------------------
Admin-only operations: view all users, freeze accounts, system stats, etc.
These functions should only be called from admin-protected routes.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Account, Transaction, TransactionType
from utils.helpers import log_event, format_currency
from typing import Optional


def get_all_users(db: Session) -> dict:
    """Returns list of all registered users with their account count."""
    users = db.query(User).all()
    return {
        "success": True,
        "total": len(users),
        "users": [
            {
                "id": u.id,
                "name": u.full_name,
                "email": u.email,
                "phone": u.phone,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "accounts": len(u.accounts),
                "joined": str(u.created_at)
            }
            for u in users
        ]
    }


def toggle_user_status(db: Session, user_id: int) -> dict:
    """
    Activates or deactivates a user account.
    Deactivated users cannot log in.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found."}

    user.is_active = not user.is_active
    db.commit()

    status = "activated" if user.is_active else "deactivated"
    log_event(f"Admin: User {user.email} {status}")
    return {"success": True, "message": f"User {user.email} has been {status}."}


def freeze_account(db: Session, account_number: str) -> dict:
    """
    Freezes a specific bank account — no transactions allowed.
    """
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        return {"success": False, "message": "Account not found."}

    account.is_active = not account.is_active
    db.commit()

    status = "unfrozen" if account.is_active else "frozen"
    log_event(f"Admin: Account {account_number} {status}")
    return {"success": True, "message": f"Account {account_number} has been {status}."}


def get_system_stats(db: Session) -> dict:
    """
    Returns key metrics for the admin dashboard.
    
    Includes:
    - Total users, accounts, transactions
    - Total money in the system
    - Breakdown by transaction type
    """
    total_users    = db.query(User).count()
    active_users   = db.query(User).filter(User.is_active == True).count()
    total_accounts = db.query(Account).count()
    total_balance  = db.query(func.sum(Account.balance)).scalar() or 0.0

    total_txns    = db.query(Transaction).count()
    deposits      = db.query(Transaction).filter(Transaction.transaction_type == TransactionType.DEPOSIT).count()
    withdrawals   = db.query(Transaction).filter(Transaction.transaction_type == TransactionType.WITHDRAWAL).count()
    transfers     = db.query(Transaction).filter(Transaction.transaction_type == TransactionType.TRANSFER).count()

    return {
        "success": True,
        "stats": {
            "users": {"total": total_users, "active": active_users, "inactive": total_users - active_users},
            "accounts": {"total": total_accounts},
            "balance": {"total_in_system": total_balance, "formatted": format_currency(total_balance)},
            "transactions": {
                "total": total_txns,
                "deposits": deposits,
                "withdrawals": withdrawals,
                "transfers": transfers
            }
        }
    }


def search_user(db: Session, query: str) -> dict:
    """
    Search users by name or email (case-insensitive partial match).
    """
    results = db.query(User).filter(
        (User.email.ilike(f"%{query}%")) | (User.full_name.ilike(f"%{query}%"))
    ).all()

    return {
        "success": True,
        "results": [
            {"id": u.id, "name": u.full_name, "email": u.email, "is_active": u.is_active}
            for u in results
        ]
    }
