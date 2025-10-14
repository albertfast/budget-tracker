from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Plaid integration fields
    plaid_access_token = Column(String, nullable=True)  # Encrypted in production
    plaid_item_id = Column(String, nullable=True)
    plaid_account_id = Column(String, nullable=True)
    
    # Bank account details
    account_name = Column(String, nullable=False)  # User-friendly label
    bank_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)  # checking, savings, credit, etc.
    account_subtype = Column(String, nullable=True)  # specific subtype from Plaid
    mask = Column(String, nullable=True)  # Last 4 digits
    
    # Account status and balances
    is_active = Column(Boolean, default=True)
    current_balance = Column(Float, default=0.0)
    available_balance = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="bank_account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bank_account_id = Column(String, ForeignKey("bank_accounts.id"), nullable=False)
    
    # Plaid transaction fields
    plaid_transaction_id = Column(String, unique=True, nullable=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)  # Positive for credits, negative for debits
    description = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Categorization
    category_primary = Column(String, nullable=True)
    category_detailed = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    
    # User customization
    user_category = Column(String, nullable=True)  # User can override category
    user_notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False)
    
    # Status
    is_pending = Column(Boolean, default=False)
    is_manual = Column(Boolean, default=False)  # User manually added
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bank_account = relationship("BankAccount", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Budget details
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount_limit = Column(Float, nullable=False)
    period = Column(String, nullable=False)  # monthly, weekly, yearly
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budgets")

class PlaidLinkSession(Base):
    """Track Plaid Link sessions for security and debugging"""
    __tablename__ = "plaid_link_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    link_token = Column(String, nullable=False)
    public_token = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    
    status = Column(String, default="created")  # created, linked, expired, error
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)