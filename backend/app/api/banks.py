from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..core.security import verify_token
from ..models.user import User
from ..models.bank_account import BankAccount
from ..models.plaid_link_session import PlaidLinkSession
from ..services.plaid_service import plaid_service
from ..services.transaction_service import transaction_service
from ..services.encryption_service import encrypt_sensitive_data, decrypt_sensitive_data

router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class LinkTokenRequest(BaseModel):
    pass

class LinkTokenResponse(BaseModel):
    link_token: str
    expiration: str

class ExchangeTokenRequest(BaseModel):
    public_token: str

class BankAccountResponse(BaseModel):
    id: str
    account_name: str
    bank_name: str
    account_type: str
    mask: Optional[str]
    current_balance: float
    available_balance: Optional[float]
    is_active: bool
    last_synced_at: Optional[datetime]

class ConnectedAccountsResponse(BaseModel):
    accounts: List[BankAccountResponse]

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/link/create-token", response_model=LinkTokenResponse)
async def create_link_token(
    request: LinkTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Plaid Link token for bank account connection"""
    try:
        # Create link token through Plaid service
        link_data = plaid_service.create_link_token(
            user_id=current_user.id,
            user_email=current_user.email
        )
        
        # Store link session in database
        link_session = PlaidLinkSession(
            user_id=current_user.id,
            link_token=link_data["link_token"],
            expires_at=datetime.fromisoformat(link_data["expiration"])
        )
        db.add(link_session)
        db.commit()
        
        return LinkTokenResponse(**link_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link token: {str(e)}"
        )

@router.post("/link/exchange-token")
async def exchange_public_token(
    request: ExchangeTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exchange public token for access token and create bank accounts"""
    try:
        # Exchange public token for access token
        token_data = plaid_service.exchange_public_token(request.public_token)
        access_token = token_data["access_token"]
        item_id = token_data["item_id"]
        
        # Get account information from Plaid
        plaid_accounts = plaid_service.get_accounts(access_token)
        
        # Create bank accounts in database
        created_accounts = []
        for plaid_account in plaid_accounts:
            bank_account = BankAccount(
                user_id=current_user.id,
                plaid_access_token=encrypt_sensitive_data(access_token),  # Encrypt access token
                plaid_item_id=item_id,
                plaid_account_id=plaid_account["account_id"],
                account_name=plaid_account["name"],
                bank_name=plaid_account.get("official_name") or plaid_account["name"],
                account_type=plaid_account["type"],
                account_subtype=plaid_account["subtype"],
                mask=plaid_account["mask"],
                current_balance=plaid_account["balances"]["current"] or 0.0,
                available_balance=plaid_account["balances"]["available"],
                last_synced_at=datetime.utcnow()
            )
            db.add(bank_account)
            created_accounts.append(bank_account)
        
        # Update link session
        link_session = db.query(PlaidLinkSession).filter(
            PlaidLinkSession.user_id == current_user.id,
            PlaidLinkSession.status == "created"
        ).first()
        
        if link_session:
            link_session.public_token = request.public_token
            link_session.access_token = access_token
            link_session.item_id = item_id
            link_session.status = "linked"
            link_session.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Successfully connected {len(created_accounts)} bank accounts",
            "accounts_count": len(created_accounts)
        }
        
    except Exception as e:
        # Update link session with error
        link_session = db.query(PlaidLinkSession).filter(
            PlaidLinkSession.user_id == current_user.id,
            PlaidLinkSession.status == "created"
        ).first()
        
        if link_session:
            link_session.status = "error"
            link_session.error_message = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect bank accounts: {str(e)}"
        )

@router.get("/accounts", response_model=ConnectedAccountsResponse)
async def get_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all connected bank accounts for the current user"""
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        BankAccount.is_active == True
    ).all()
    
    account_responses = [
        BankAccountResponse(
            id=account.id,
            account_name=account.account_name,
            bank_name=account.bank_name,
            account_type=account.account_type,
            mask=account.mask,
            current_balance=account.current_balance,
            available_balance=account.available_balance,
            is_active=account.is_active,
            last_synced_at=account.last_synced_at
        )
        for account in accounts
    ]
    
    return ConnectedAccountsResponse(accounts=account_responses)

@router.post("/accounts/{account_id}/sync")
async def sync_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync transactions for a specific bank account"""
    # Get the bank account
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id,
        BankAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    try:
        # Decrypt access token for API call
        decrypted_token = decrypt_sensitive_data(account.plaid_access_token)
        
        # Sync transactions from Plaid
        sync_data = plaid_service.sync_transactions(decrypted_token)
        
        # Process and save transactions to database
        processing_result = transaction_service.process_plaid_transactions(
            db, account, sync_data["transactions"]
        )
        
        # Update last synced timestamp
        account.last_synced_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"Successfully synced {processing_result['processed_count']} new transactions",
            "new_transactions": processing_result["processed_count"],
            "updated_transactions": processing_result["updated_count"],
            "total_amount": processing_result["total_amount"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync account: {str(e)}"
        )

@router.put("/accounts/{account_id}/label")
async def update_account_label(
    account_id: str,
    new_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the user-friendly label for a bank account"""
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    account.account_name = new_name
    account.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Account label updated successfully"}

@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect (deactivate) a bank account"""
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    # Soft delete - deactivate instead of removing
    account.is_active = False
    account.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Bank account disconnected successfully"}