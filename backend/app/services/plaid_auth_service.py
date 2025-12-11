"""
Plaid Authentication & Data Sync Service (v2019)
Handles Plaid login flow and syncs income/expense data to dashboard
PostgreSQL optimized with proper transaction handling and connection pooling
"""

import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

# Plaid 2019 API client
from plaid.client import Client

from ..models.user import User
from ..models.bank_account import BankAccount
from ..models.transaction import Transaction
from ..models.plaid_link_session import PlaidLinkSession

logger = logging.getLogger(__name__)
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_PUBLIC_KEY = os.getenv("PLAID_PUBLIC_KEY")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

# Transaction sync settings
DEFAULT_TRANSACTION_DAYS = 90  # Fetch last 90 days of transactions
INCOME_KEYWORDS = ["salary", "paycheck", "deposit", "transfer", "refund", "bonus", "income"]
EXPENSE_KEYWORDS = ["purchase", "payment", "withdrawal", "debit", "charge", "fee"]


def _get_client() -> Client:
    """Initialize the legacy Plaid client."""
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        logger.warning("PLAID credentials missing")
    
    return Client(
        client_id=PLAID_CLIENT_ID,
        secret=PLAID_SECRET,
        public_key=PLAID_PUBLIC_KEY,
        environment=PLAID_ENV,
    )


def create_plaid_link_session(user_id: str, db: Session) -> str:
    """
    Create a Plaid Link session for user login.
    PostgreSQL: Uses timezone-aware datetime and proper transaction handling.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # In legacy Plaid (2019), we use the public_key directly
        # The front-end initializes Plaid Link with this key
        link_token = PLAID_PUBLIC_KEY
        
        # Use timezone-aware datetime for PostgreSQL
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(hours=1)
        
        # Save session to database
        session = PlaidLinkSession(
            user_id=user_id,
            link_token=link_token,
            status="created",
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created Plaid Link session {session.id} for user {user_id}")
        return str(session.id)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create Plaid Link session for user {user_id}: {e}", exc_info=True)
        raise


def complete_plaid_login(user_id: str, public_token: str, 
                         db: Session) -> Dict[str, Any]:
    """
    Complete Plaid login flow.
    PostgreSQL optimized with proper transaction handling and rollback support.
    
    Steps:
    1. Exchange public_token for access_token
    2. Fetch and store bank accounts
    3. Sync transactions
    4. Update dashboard
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        client = _get_client()
        
        # Step 1: Exchange public_token for access_token
        exchange_resp = client.Item.public_token.exchange(public_token)
        access_token = exchange_resp.get("access_token")
        item_id = exchange_resp.get("item_id")
        
        if not access_token:
            raise ValueError("Failed to obtain access_token from Plaid")
        
        logger.info(f"Successfully exchanged public_token for user {user_id}, item_id={item_id}")
        
        # Step 2: Fetch accounts and store them
        accounts_resp = client.Accounts.get(access_token)
        accounts = accounts_resp.get("accounts", [])
        institution_info = accounts_resp.get("item", {}).get("institution", {})
        bank_name = institution_info.get("name", "Unknown Bank")
        
        stored_accounts = []
        for account in accounts:
            bank_account = BankAccount(
                user_id=user_id,
                plaid_access_token=access_token,
                plaid_item_id=item_id,
                plaid_account_id=account.get("account_id"),
                account_name=account.get("name", "Unknown Account"),
                bank_name=bank_name,
                account_type=account.get("subtype", "unknown"),
                account_subtype=account.get("subtype"),
                mask=account.get("mask"),
                current_balance=float(account.get("balances", {}).get("current", 0.0)),
                available_balance=float(account.get("balances", {}).get("available", 0.0)),
                is_active=True,
                last_synced_at=datetime.now(timezone.utc)
            )
            db.add(bank_account)
            stored_accounts.append(bank_account)
        
        db.commit()
        logger.info(f"Stored {len(stored_accounts)} bank accounts for user {user_id}")
        
        # Step 3: Sync transactions
        sync_result = sync_plaid_transactions(user_id, access_token, db)
        
        return {
            "success": True,
            "user_id": user_id,
            "access_token": access_token,
            "item_id": item_id,
            "accounts_count": len(stored_accounts),
            "transactions_synced": sync_result["total_synced"],
            "accounts": [
                {
                    "id": str(acc.id),
                    "name": acc.account_name,
                    "type": acc.account_type,
                    "mask": acc.mask,
                    "balance": round(acc.current_balance, 2),
                    "available": round(acc.available_balance or 0.0, 2)
                }
                for acc in stored_accounts
            ]
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to complete Plaid login for user {user_id}: {e}", exc_info=True)
        raise


def sync_plaid_transactions(user_id: str, access_token: str, 
                           db: Session, days: int = DEFAULT_TRANSACTION_DAYS) -> Dict[str, Any]:
    """
    Sync Plaid transactions to PostgreSQL database.
    Categorizes as income or expense based on keywords.
    Optimized for PostgreSQL with bulk operations and proper timezone handling.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        client = _get_client()
        
        # Use timezone-aware datetime for PostgreSQL
        now_utc = datetime.now(timezone.utc)
        end_date = now_utc.date()
        start_date = end_date - timedelta(days=days)
        
        # Fetch all transactions
        transactions_resp = client.Transactions.get(
            access_token,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        transactions = transactions_resp.get("transactions", [])
        total_synced = 0
        income_count = 0
        expense_count = 0
        skipped_count = 0
        
        # Get user's bank accounts to link transactions
        # Use explicit load for performance
        user_accounts = db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.is_active == True
        ).all()
        
        account_map = {acc.plaid_account_id: acc.id for acc in user_accounts}
        
        # Prepare transactions for batch insert
        transactions_to_add = []
        
        for trans in transactions:
            plaid_trans_id = trans.get("transaction_id")
            
            # Check if already synced (prevent duplicates in PostgreSQL)
            existing = db.query(Transaction).filter(
                Transaction.plaid_transaction_id == plaid_trans_id
            ).first()
            if existing:
                skipped_count += 1
                continue
            
            # Get bank account
            plaid_account_id = trans.get("account_id")
            bank_account_id = account_map.get(plaid_account_id)
            if not bank_account_id:
                logger.warning(f"Account {plaid_account_id} not found for transaction {plaid_trans_id}")
                continue
            
            # Categorize transaction
            description = trans.get("name", "")
            amount = float(trans.get("amount", 0.0))
            
            # Determine if income or expense
            category_primary = _categorize_transaction(description, amount)
            
            if "income" in category_primary.lower():
                income_count += 1
            elif "expense" in category_primary.lower():
                expense_count += 1
            
            # Parse date safely
            try:
                trans_date = datetime.fromisoformat(trans.get("date"))
                # Ensure timezone-aware for PostgreSQL
                if trans_date.tzinfo is None:
                    trans_date = trans_date.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                logger.warning(f"Invalid transaction date for {plaid_trans_id}: {trans.get('date')}")
                trans_date = now_utc
            
            # Create transaction record
            transaction = Transaction(
                bank_account_id=str(bank_account_id),
                plaid_transaction_id=plaid_trans_id,
                amount=amount,
                description=description,
                date=trans_date,
                category_primary=category_primary,
                category_detailed=trans.get("personal_finance_category", category_primary),
                merchant_name=trans.get("merchant_name", description),
                is_pending=trans.get("pending", False),
                is_manual=False
            )
            
            transactions_to_add.append(transaction)
            total_synced += 1
        
        # Bulk add transactions
        if transactions_to_add:
            db.add_all(transactions_to_add)
            db.commit()
        
        logger.info(
            f"Synced {total_synced} transactions for user {user_id} "
            f"(Income: {income_count}, Expenses: {expense_count}, Skipped: {skipped_count}) "
            f"Date range: {start_date} to {end_date}"
        )
        
        return {
            "total_synced": total_synced,
            "income_count": income_count,
            "expense_count": expense_count,
            "skipped_count": skipped_count,
            "date_range": f"{start_date} to {end_date}"
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to sync transactions for user {user_id}: {e}", exc_info=True)
        raise


def _categorize_transaction(description: str, amount: float) -> str:
    """
    Categorize transaction as Income or Expense.
    Uses simple keyword matching.
    """
    desc_lower = description.lower()
    
    # Income categorization
    for keyword in INCOME_KEYWORDS:
        if keyword in desc_lower:
            return "Income"
    
    # Expense categorization (default for negative amounts)
    if amount < 0:
        return "Expense"
    
    # Default to income for positive amounts
    return "Income"


def get_user_financial_summary(user_id: str, db: Session,
                               days: int = 30) -> Dict[str, Any]:
    """
    Get financial summary for dashboard.
    PostgreSQL optimized with proper joins and aggregation.
    Returns income/expense totals for the specified period.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Use timezone-aware datetime for PostgreSQL
        now_utc = datetime.now(timezone.utc)
        end_date = now_utc
        start_date = end_date - timedelta(days=days)
        
        # Get transactions for this period using optimized query
        transactions = db.query(Transaction).join(
            BankAccount, Transaction.bank_account_id == BankAccount.id
        ).filter(
            BankAccount.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_manual == False  # Only Plaid-synced transactions
        ).order_by(Transaction.date.desc()).all()
        
        # Calculate totals by category using Python aggregation
        income_total = 0.0
        expense_total = 0.0
        by_category = {}
        
        for trans in transactions:
            amount = trans.amount
            category = trans.category_primary or "Uncategorized"
            
            # Track category totals
            if category not in by_category:
                by_category[category] = {
                    "count": 0,
                    "total": 0.0,
                    "average": 0.0
                }
            
            by_category[category]["count"] += 1
            by_category[category]["total"] += amount
            
            # Income vs Expense
            if "income" in category.lower():
                income_total += amount
            elif "expense" in category.lower() or amount < 0:
                expense_total += abs(amount)
        
        # Calculate averages
        for category in by_category:
            count = by_category[category]["count"]
            if count > 0:
                by_category[category]["average"] = by_category[category]["total"] / count
        
        net_income = income_total - expense_total
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_transactions": len(transactions),
            "income_total": round(income_total, 2),
            "expense_total": round(expense_total, 2),
            "net_income": round(net_income, 2),
            "by_category": {
                cat: {
                    "count": data["count"],
                    "total": round(data["total"], 2),
                    "average": round(data["average"], 2)
                }
                for cat, data in by_category.items()
            },
            "transactions": [
                {
                    "id": str(t.id),
                    "description": t.description,
                    "amount": round(t.amount, 2),
                    "category": t.category_primary,
                    "date": t.date.isoformat()
                }
                for t in transactions[:20]  # Last 20 transactions
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get financial summary for user {user_id}: {e}", exc_info=True)
        raise


def refresh_plaid_tokens(user_id: str, db: Session) -> Dict[str, Any]:
    """
    Refresh Plaid data for user by re-syncing transactions.
    Called periodically or on demand.
    PostgreSQL optimized with proper transaction handling.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get user's access token from their first active bank account
        bank_account = db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.is_active == True,
            BankAccount.plaid_access_token != None
        ).first()
        
        if not bank_account or not bank_account.plaid_access_token:
            raise ValueError("No active Plaid account linked for this user")
        
        # Sync transactions
        sync_result = sync_plaid_transactions(
            user_id,
            bank_account.plaid_access_token,
            db
        )
        
        # Update last synced timestamp for all user's accounts
        now_utc = datetime.now(timezone.utc)
        db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.is_active == True
        ).update(
            {BankAccount.last_synced_at: now_utc},
            synchronize_session=False
        )
        db.commit()
        
        logger.info(f"Successfully refreshed Plaid data for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "sync_result": sync_result,
            "last_synced": now_utc.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to refresh tokens for user {user_id}: {e}", exc_info=True)
        raise
