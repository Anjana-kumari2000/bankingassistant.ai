"""
utils/security.py
-----------------
Handles password hashing and JWT token creation/verification.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Secret key for JWT signing — in production, use a long random string from env variable
SECRET_KEY = "banking_secret_key_change_in_production"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token valid for 1 hour

# CryptContext: uses bcrypt algorithm to hash passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Example: hash_password("mypassword") → "$2b$12$..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain password with the stored hash.
    Returns True if they match.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token containing user data.
    
    data: dict like {"sub": "user@email.com"}
    expires_delta: how long until token expires
    
    Returns: encoded JWT string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decodes and verifies a JWT token.
    Returns the payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
