from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

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
