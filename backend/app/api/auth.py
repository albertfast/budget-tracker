from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Dict, Any

from ..core.database import get_db
from ..core.security import verify_password, get_password_hash, create_access_token, verify_token
from ..models.user import User
from ..services.plaid_auth_service import (
    create_plaid_link_session,
    complete_plaid_login,
    get_user_financial_summary,
    refresh_plaid_tokens
)

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at
    )


# ============================================================================
# PLAID AUTHENTICATION ENDPOINTS (v2019)
# ============================================================================

class PlaidLinkInitResponse(BaseModel):
    """Response for initializing Plaid Link"""
    session_id: str
    public_key: str
    environment: str
    products: list
    country_codes: list


class PlaidCompleteLoginRequest(BaseModel):
    """Request to complete Plaid login"""
    user_id: str
    public_token: str


class PlaidCompleteLoginResponse(BaseModel):
    """Response after completing Plaid login"""
    success: bool
    user_id: str
    access_token: str
    item_id: str
    accounts_count: int
    transactions_synced: int
    accounts: list


class FinancialSummaryResponse(BaseModel):
    """Financial summary for dashboard"""
    period_days: int
    start_date: str
    end_date: str
    total_transactions: int
    income_total: float
    expense_total: float
    net_income: float
    by_category: Dict[str, Any]
    transactions: list


@router.post("/plaid/link-init", response_model=PlaidLinkInitResponse)
async def init_plaid_link(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Initialize Plaid Link for user login.
    Returns public_key and configuration for front-end Plaid Link initialization.
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create Plaid Link session
        session_id = create_plaid_link_session(user_id, db)
        
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        return PlaidLinkInitResponse(
            session_id=session_id,
            public_key=os.getenv("PLAID_PUBLIC_KEY"),
            environment=os.getenv("PLAID_ENV", "sandbox"),
            products=["transactions"],
            country_codes=["US"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize Plaid Link: {str(e)}"
        )


@router.post("/plaid/complete-login", response_model=PlaidCompleteLoginResponse)
async def complete_plaid_login_endpoint(
    request: PlaidCompleteLoginRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Complete Plaid login flow.
    Exchanges public_token for access_token and syncs financial data.
    ONLY works if user is authenticated with valid credentials.
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ensure user_id in request matches authenticated user
        if request.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot complete login for different user"
            )
        
        # Complete Plaid login
        result = complete_plaid_login(user_id, request.public_token, db)
        
        return PlaidCompleteLoginResponse(
            success=result["success"],
            user_id=result["user_id"],
            access_token=result["access_token"],
            item_id=result["item_id"],
            accounts_count=result["accounts_count"],
            transactions_synced=result["transactions_synced"],
            accounts=result["accounts"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to complete Plaid login: {str(e)}"
        )


@router.get("/financial-summary", response_model=FinancialSummaryResponse)
async def get_financial_summary(
    days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get financial summary for authenticated user.
    Returns income/expense totals and transactions synced from Plaid.
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get financial summary
        summary = get_user_financial_summary(user_id, db, days=days)
        
        return FinancialSummaryResponse(
            period_days=summary["period_days"],
            start_date=summary["start_date"],
            end_date=summary["end_date"],
            total_transactions=summary["total_transactions"],
            income_total=summary["income_total"],
            expense_total=summary["expense_total"],
            net_income=summary["net_income"],
            by_category=summary["by_category"],
            transactions=summary["transactions"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get financial summary: {str(e)}"
        )


@router.post("/plaid/refresh")
async def refresh_plaid_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Manually refresh Plaid data for authenticated user.
    Re-syncs transactions from connected financial institutions.
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Refresh tokens and sync
        result = refresh_plaid_tokens(user_id, db)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh Plaid data: {str(e)}"
        )