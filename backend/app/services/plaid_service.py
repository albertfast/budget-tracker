import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class PlaidService:
    """Service class for Plaid API integration"""
    
    def __init__(self):
        # Resolve environment robustly across plaid-python versions
        env_name = (settings.PLAID_ENV or "sandbox").lower()
        env_mapping = {
            "sandbox": "Sandbox",
            "development": "Development",
            "production": "Production",
        }
        resolved_host = None
        # Try plaid.Environment first
        if hasattr(plaid, "Environment"):
            resolved_host = getattr(plaid.Environment, env_mapping.get(env_name, "Sandbox"), plaid.Environment.Sandbox)
        # Fallback to PlaidEnvironments if present (some SDK variants)
        if resolved_host is None and hasattr(plaid, "PlaidEnvironments"):
            resolved_host = getattr(plaid.PlaidEnvironments, env_mapping.get(env_name, "Sandbox"), plaid.PlaidEnvironments.Sandbox)

        self.configuration = Configuration(
            host=resolved_host,
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        self.api_client = ApiClient(self.configuration)
        self.client = plaid_api.PlaidApi(self.api_client)
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Coerce Plaid SDK response objects to plain dicts safely."""
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "to_dict"):
            try:
                return obj.to_dict()
            except Exception:
                pass
        # Best-effort fallback via __dict__
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_") and not callable(getattr(obj, k))}
    
    def create_link_token(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization"""
        try:
            request = LinkTokenCreateRequest(
                products=[Products(prod) for prod in settings.PLAID_PRODUCTS],
                client_name=settings.PROJECT_NAME,
                country_codes=[CountryCode(cc) for cc in settings.PLAID_COUNTRY_CODES],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )
            response = self.client.link_token_create(request)
            data = self._to_dict(response)
            return {
                "link_token": data.get("link_token"),
                "expiration": data.get("expiration"),
            }
        except Exception as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise Exception(f"Failed to create link token: {str(e)}")
    
    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """Exchange public token for access token"""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            data = self._to_dict(response)
            return {
                "access_token": data.get("access_token"),
                "item_id": data.get("item_id"),
            }
        except Exception as e:
            logger.error(f"Error exchanging public token: {str(e)}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch account information from Plaid"""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            data = self._to_dict(response)
            accounts_raw = data.get("accounts", [])
            accounts = []
            for account in accounts_raw:
                a = account if isinstance(account, dict) else self._to_dict(account)
                bal = a.get("balances", {}) if isinstance(a.get("balances"), dict) else self._to_dict(a.get("balances", {}))
                accounts.append({
                    "account_id": a.get("account_id"),
                    "name": a.get("name"),
                    "official_name": a.get("official_name"),
                    "type": a.get("type"),
                    "subtype": a.get("subtype"),
                    "mask": a.get("mask"),
                    "balances": {
                        "current": bal.get("current"),
                        "available": bal.get("available"),
                        "limit": bal.get("limit"),
                    },
                })
            
            return accounts
        except Exception as e:
            logger.error(f"Error fetching accounts: {str(e)}")
            raise Exception(f"Failed to fetch accounts: {str(e)}")
    
    def get_transactions(
        self, 
        access_token: str, 
        start_date: datetime, 
        end_date: datetime,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch transactions from Plaid"""
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                account_ids=account_ids
            )
            response = self.client.transactions_get(request)
            data = self._to_dict(response)
            tx_raw = data.get("transactions", [])
            transactions = []
            for transaction in tx_raw:
                t = transaction if isinstance(transaction, dict) else self._to_dict(transaction)
                transactions.append({
                    "transaction_id": t.get("transaction_id"),
                    "account_id": t.get("account_id"),
                    "amount": t.get("amount"),
                    "date": t.get("date"),
                    "name": t.get("name"),
                    "merchant_name": t.get("merchant_name"),
                    "category": t.get("category", []),
                    "category_id": t.get("category_id"),
                    "account_owner": t.get("account_owner"),
                    "pending": t.get("pending", False),
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise Exception(f"Failed to fetch transactions: {str(e)}")
    
    def sync_transactions(
        self, 
        access_token: str, 
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync transactions using Plaid's sync endpoint (more efficient for updates)"""
        try:
            # This would use the transactions/sync endpoint for incremental updates
            # For now, we'll use the regular transactions endpoint
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days
            
            transactions = self.get_transactions(access_token, start_date, end_date)
            
            return {
                "transactions": transactions,
                "has_more": False,  # Simplified for this implementation
                "next_cursor": None
            }
        except Exception as e:
            logger.error(f"Error syncing transactions: {str(e)}")
            raise Exception(f"Failed to sync transactions: {str(e)}")

# Initialize Plaid service
plaid_service = PlaidService()