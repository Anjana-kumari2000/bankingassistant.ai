"""
routes/user.py
--------------
User-facing API endpoints: register, login, profile.
Prefix: /user
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_db
from services import auth_service
from utils.security import decode_token

router = APIRouter(prefix="/user", tags=["User"])


# ─── Pydantic Schemas (request body models) ───────────────────────────────────

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─── Helper: get current user from Authorization header ───────────────────────

def get_current_user_from_token(
    authorization: str = Header(...),  # expects: "Bearer <token>"
    db: Session = Depends(get_db)
):
    """
    Dependency function — extracts and verifies token from request header.
    Used in protected routes with: current_user = Depends(get_current_user_from_token)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format.")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    
    user = auth_service.get_current_user(db, payload)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    
    return user


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    POST /user/register
    Creates a new user account.
    
    Request body:
        { "full_name": "John", "email": "john@example.com", "password": "secret" }
    """
    result = auth_service.register_user(
        db, data.full_name, data.email, data.password, data.phone
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    POST /user/login
    Returns JWT token on successful authentication.
    """
    result = auth_service.login_user(db, data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@router.get("/profile")
def get_profile(current_user=Depends(get_current_user_from_token)):
    """
    GET /user/profile
    Returns profile of the currently authenticated user.
    Requires: Authorization: Bearer <token>
    """
    return {
        "id": current_user.id,
        "name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "joined": str(current_user.created_at),
        "accounts": [
            {
                "account_number": acc.account_number,
                "type": acc.account_type.value,
                "balance": acc.balance
            }
            for acc in current_user.accounts
        ]
    }
