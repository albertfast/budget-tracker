from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

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
