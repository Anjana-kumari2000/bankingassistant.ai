"""
services/auth_service.py
------------------------
Handles user registration, login, and token-based authentication.
Business logic lives here — routes just call these functions.
"""

from sqlalchemy.orm import Session
from models import User, Account
from utils.security import hash_password, verify_password, create_access_token
from utils.helpers import generate_account_number, log_event
from typing import Optional


def register_user(db: Session, full_name: str, email: str, password: str, phone: str = None) -> dict:
    """
    Creates a new user and their first savings account.
    
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Create User record
    4. Auto-create a savings account for them
    5. Return success message
    """
    # Step 1: Check for duplicate email
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"success": False, "message": "Email already registered."}

    # Step 2 & 3: Create user with hashed password
    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        phone=phone
    )
    db.add(new_user)
    db.flush()  # flush to get new_user.id without full commit

    # Step 4: Auto-create savings account
    account = Account(
        account_number=generate_account_number(),
        user_id=new_user.id,
        balance=0.0
    )
    db.add(account)
    db.commit()
    db.refresh(new_user)

    log_event(f"New user registered: {email}")
    return {
        "success": True,
        "message": "Registration successful.",
        "account_number": account.account_number
    }


def login_user(db: Session, email: str, password: str) -> dict:
    """
    Validates credentials and returns a JWT token.
    
    Returns:
        {"success": True, "token": "...", "user": {...}}
        or
        {"success": False, "message": "..."}
    """
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        log_event(f"Failed login attempt for: {email}")
        return {"success": False, "message": "Invalid email or password."}

    if not user.is_active:
        return {"success": False, "message": "Account is deactivated. Contact admin."}

    # Create JWT token with user email as subject
    token = create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    log_event(f"User logged in: {email}")

    return {
        "success": True,
        "token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetches a user by email. Used in token verification."""
    return db.query(User).filter(User.email == email).first()


def get_current_user(db: Session, token_payload: dict) -> Optional[User]:
    """
    Given a decoded JWT payload, returns the User object.
    Used as a dependency in protected routes.
    """
    email = token_payload.get("sub")
    if not email:
        return None
    return get_user_by_email(db, email)
