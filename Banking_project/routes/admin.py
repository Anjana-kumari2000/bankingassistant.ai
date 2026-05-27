"""
routes/admin.py
---------------
Admin-only API endpoints.
Protected by: is_admin check on the current user.
Prefix: /admin
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services import admin_service
from routes.user import get_current_user_from_token

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user=Depends(get_current_user_from_token)):
    """
    Dependency: raises 403 if the user is not an admin.
    All admin routes use: Depends(require_admin)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """GET /admin/users — List all users in the system."""
    return admin_service.get_all_users(db)


@router.put("/users/{user_id}/toggle")
def toggle_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """PUT /admin/users/{id}/toggle — Activate or deactivate a user."""
    return admin_service.toggle_user_status(db, user_id)


@router.put("/accounts/{account_number}/freeze")
def freeze_account(account_number: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """PUT /admin/accounts/{acc}/freeze — Freeze or unfreeze an account."""
    return admin_service.freeze_account(db, account_number)


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """GET /admin/stats — System-wide metrics."""
    return admin_service.get_system_stats(db)


@router.get("/search")
def search_user(query: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """GET /admin/search?query=john — Search users by name or email."""
    return admin_service.search_user(db, query)
