from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from ..core.database import Base
import uuid

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
