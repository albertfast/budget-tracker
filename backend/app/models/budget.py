from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

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
