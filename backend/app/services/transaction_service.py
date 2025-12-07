from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..models.transaction import Transaction
from ..models.bank_account import BankAccount
from ..models.user import User
from ..services.plaid_service import plaid_service
from .encryption_service import encrypt_sensitive_data, decrypt_sensitive_data
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """Service for processing and analyzing bank transactions"""
    
    def __init__(self):
        self.category_mappings = self._load_category_mappings()
        self.merchant_patterns = self._load_merchant_patterns()
    
    def process_plaid_transactions(
        self, 
        db: Session, 
        bank_account: BankAccount, 
        plaid_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process transactions from Plaid and save to database"""
        try:
            processed_count = 0
            updated_count = 0
            new_transactions = []
            
            for plaid_tx in plaid_transactions:
                # Check if transaction already exists
                existing_tx = db.query(Transaction).filter(
                    Transaction.plaid_transaction_id == plaid_tx["transaction_id"]
                ).first()
                
                if existing_tx:
                    # Update existing transaction if needed
                    if self._should_update_transaction(existing_tx, plaid_tx):
                        self._update_transaction_from_plaid(existing_tx, plaid_tx)
                        updated_count += 1
                else:
                    # Create new transaction
                    transaction = self._create_transaction_from_plaid(bank_account, plaid_tx)
                    db.add(transaction)
                    new_transactions.append(transaction)
                    processed_count += 1
            
            db.commit()
            
            # Update account balance if we have current balance info
            if hasattr(bank_account, 'current_balance'):
                bank_account.last_synced_at = datetime.utcnow()
                db.commit()
            
            return {
                "processed_count": processed_count,
                "updated_count": updated_count,
                "new_transactions": new_transactions,
                "total_amount": sum(tx.amount for tx in new_transactions)
            }
            
        except Exception as e:
            logger.error(f"Error processing transactions: {str(e)}")
            db.rollback()
            raise Exception(f"Failed to process transactions: {str(e)}")
    
    def _create_transaction_from_plaid(
        self, 
        bank_account: BankAccount, 
        plaid_tx: Dict[str, Any]
    ) -> Transaction:
        """Create Transaction object from Plaid transaction data"""
        
        # Process amount (Plaid amounts are positive for outflows, negative for inflows)
        amount = -plaid_tx["amount"]  # Invert to match our convention
        
        # Extract and clean merchant name
        merchant_name = self._extract_merchant_name(plaid_tx)
        
        # Categorize transaction
        category_info = self._categorize_transaction(plaid_tx, merchant_name)
        
        # Parse transaction date
        tx_date = datetime.strptime(plaid_tx["date"], "%Y-%m-%d")
        
        return Transaction(
            bank_account_id=bank_account.id,
            plaid_transaction_id=plaid_tx["transaction_id"],
            amount=amount,
            description=plaid_tx["name"],
            date=tx_date,
            category_primary=category_info["primary"],
            category_detailed=category_info["detailed"],
            merchant_name=merchant_name,
            is_pending=plaid_tx.get("pending", False),
            is_manual=False
        )
    
    def _extract_merchant_name(self, plaid_tx: Dict[str, Any]) -> Optional[str]:
        """Extract and clean merchant name from transaction"""
        # Try merchant_name field first
        if plaid_tx.get("merchant_name"):
            return self._clean_merchant_name(plaid_tx["merchant_name"])
        
        # Fallback to parsing from transaction name
        tx_name = plaid_tx["name"]
        
        # Remove common prefixes and suffixes
        cleaned_name = re.sub(r'^(DEBIT|CREDIT|POS|ATM|ONLINE|RECURRING)\s+', '', tx_name, flags=re.IGNORECASE)
        cleaned_name = re.sub(r'\s+(PURCHASE|PAYMENT|WITHDRAWAL|DEPOSIT)\s*$', '', cleaned_name, flags=re.IGNORECASE)
        
        # Extract merchant from patterns
        for pattern, merchant in self.merchant_patterns.items():
            if re.search(pattern, cleaned_name, re.IGNORECASE):
                return merchant
        
        return cleaned_name.strip() if len(cleaned_name.strip()) > 3 else None
    
    def _clean_merchant_name(self, merchant_name: str) -> str:
        """Clean and standardize merchant names"""
        # Remove location info and standardize
        cleaned = re.sub(r'\s+#\d+', '', merchant_name)  # Remove store numbers
        cleaned = re.sub(r'\s+\d{4,}', '', cleaned)  # Remove long numbers
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)  # Normalize spaces
        return cleaned.strip().title()
    
    def _categorize_transaction(
        self, 
        plaid_tx: Dict[str, Any], 
        merchant_name: Optional[str]
    ) -> Dict[str, str]:
        """Categorize transaction based on Plaid categories and merchant"""
        
        # Get Plaid categories
        plaid_categories = plaid_tx.get("category", [])
        primary_category = plaid_categories[0] if plaid_categories else "Other"
        detailed_category = plaid_categories[-1] if len(plaid_categories) > 1 else primary_category
        
        # Enhance categorization with merchant-based rules
        if merchant_name:
            enhanced_category = self._enhance_category_with_merchant(merchant_name, primary_category)
            if enhanced_category:
                primary_category = enhanced_category
        
        return {
            "primary": primary_category,
            "detailed": detailed_category
        }
    
    def _enhance_category_with_merchant(self, merchant_name: str, current_category: str) -> Optional[str]:
        """Enhance categorization using merchant name patterns"""
        merchant_lower = merchant_name.lower()
        
        # Grocery stores
        if any(term in merchant_lower for term in ['grocery', 'market', 'food', 'kroger', 'walmart', 'target']):
            return "Food and Drink"
        
        # Gas stations
        if any(term in merchant_lower for term in ['gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron']):
            return "Transportation"
        
        # Restaurants
        if any(term in merchant_lower for term in ['restaurant', 'cafe', 'coffee', 'pizza', 'burger']):
            return "Food and Drink"
        
        # Shopping
        if any(term in merchant_lower for term in ['amazon', 'store', 'shop', 'retail']):
            return "Shops"
        
        return None
    
    def _should_update_transaction(self, existing_tx: Transaction, plaid_tx: Dict[str, Any]) -> bool:
        """Check if existing transaction should be updated"""
        # Update if pending status changed or amount changed
        return (
            existing_tx.is_pending != plaid_tx.get("pending", False) or
            abs(existing_tx.amount + plaid_tx["amount"]) > 0.01  # Account for floating point precision
        )
    
    def _update_transaction_from_plaid(self, transaction: Transaction, plaid_tx: Dict[str, Any]):
        """Update existing transaction with Plaid data"""
        transaction.amount = -plaid_tx["amount"]
        transaction.is_pending = plaid_tx.get("pending", False)
        transaction.updated_at = datetime.utcnow()
    
    def get_spending_analysis(
        self, 
        db: Session, 
        user_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive spending analysis for user"""
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user's transactions
        transactions = db.query(Transaction).join(BankAccount).filter(
            BankAccount.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount < 0  # Only expenses
        ).all()
        
        # Analyze spending by category
        category_spending = defaultdict(float)
        merchant_spending = defaultdict(float)
        daily_spending = defaultdict(float)
        
        total_spent = 0
        transaction_count = 0
        
        for tx in transactions:
            amount = abs(tx.amount)
            total_spent += amount
            transaction_count += 1
            
            # Category analysis
            category_spending[tx.category_primary or "Other"] += amount
            
            # Merchant analysis
            if tx.merchant_name:
                merchant_spending[tx.merchant_name] += amount
            
            # Daily spending
            day_key = tx.date.strftime("%Y-%m-%d")
            daily_spending[day_key] += amount
        
        # Calculate averages and insights
        avg_daily_spend = total_spent / days if days > 0 else 0
        avg_transaction_amount = total_spent / transaction_count if transaction_count > 0 else 0
        
        # Top categories and merchants
        top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "period_days": days,
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "avg_daily_spend": avg_daily_spend,
            "avg_transaction_amount": avg_transaction_amount,
            "category_breakdown": dict(category_spending),
            "top_categories": top_categories,
            "top_merchants": top_merchants,
            "daily_spending": dict(daily_spending)
        }
    
    def detect_recurring_transactions(
        self, 
        db: Session, 
        user_id: str, 
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """Detect recurring transactions and subscriptions"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions grouped by merchant and amount
        transactions = db.query(Transaction).join(BankAccount).filter(
            BankAccount.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.merchant_name.isnot(None),
            Transaction.amount < 0  # Only expenses
        ).all()
        
        # Group by merchant and similar amounts
        merchant_amounts = defaultdict(list)
        
        for tx in transactions:
            key = (tx.merchant_name, round(abs(tx.amount), 2))
            merchant_amounts[key].append(tx)
        
        # Find recurring patterns
        recurring_transactions = []
        
        for (merchant, amount), tx_list in merchant_amounts.items():
            if len(tx_list) >= 2:  # At least 2 occurrences
                # Calculate frequency
                dates = sorted([tx.date for tx in tx_list])
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    
                    # Consider it recurring if roughly monthly, weekly, or yearly
                    if 25 <= avg_interval <= 35 or 6 <= avg_interval <= 8 or 360 <= avg_interval <= 370:
                        recurring_transactions.append({
                            "merchant": merchant,
                            "amount": amount,
                            "frequency": "monthly" if 25 <= avg_interval <= 35 else 
                                       "weekly" if 6 <= avg_interval <= 8 else "yearly",
                            "avg_interval_days": avg_interval,
                            "occurrence_count": len(tx_list),
                            "last_transaction": max(dates),
                            "total_spent": amount * len(tx_list)
                        })
        
        return sorted(recurring_transactions, key=lambda x: x["total_spent"], reverse=True)
    
    def _load_category_mappings(self) -> Dict[str, str]:
        """Load category mappings for enhanced categorization"""
        return {
            # Add custom category mappings here
            "streaming": "Entertainment",
            "subscription": "Entertainment",
            "gym": "Recreation",
            "fitness": "Recreation"
        }
    
    def _load_merchant_patterns(self) -> Dict[str, str]:
        """Load merchant name patterns for recognition"""
        return {
            r"SPOTIFY|NETFLIX|HULU|DISNEY": "Entertainment",
            r"STARBUCKS|DUNKIN": "Coffee Shop",
            r"UBER|LYFT": "Rideshare",
            r"AMAZON|AMZN": "Amazon",
            r"WALMART|TARGET": "Retail"
        }

# Initialize transaction processor
transaction_service = TransactionProcessor()