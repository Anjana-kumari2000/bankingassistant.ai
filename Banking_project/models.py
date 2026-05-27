from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class TransactionType(str, enum.Enum):
    DEPOSIT    = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER   = "transfer"

class TransactionStatus(str, enum.Enum):
    PENDING   = "pending"
    COMPLETED = "completed"
    FAILED    = "failed"

class AccountType(str, enum.Enum):
    SAVINGS  = "savings"
    CHECKING = "checking"


class User(Base):
    """
    Stores all registered bank users.
    One User can have many Accounts.
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    full_name     = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone         = Column(String, nullable=True)
    is_active     = Column(Boolean, default=True)
    is_admin      = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    
    accounts = relationship("Account", back_populates="owner")




class Account(Base):
    """
    A user can have multiple accounts (savings, checking).
    Each account has a unique account_number.
    """
    __tablename__ = "accounts"

    id             = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type   = Column(Enum(AccountType), default=AccountType.SAVINGS)
    balance        = Column(Float, default=0.0)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner   = relationship("User", back_populates="accounts")

    
    transactions = relationship("Transaction", back_populates="account")




class Transaction(Base):
    """
    Records every financial event: deposit, withdrawal, transfer.
    """
    __tablename__ = "transactions"

    id               = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount           = Column(Float, nullable=False)
    status           = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description      = Column(String, nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account    = relationship("Account", back_populates="transactions")

    
    target_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
