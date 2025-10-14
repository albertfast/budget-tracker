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
        self.configuration = Configuration(
            host=getattr(plaid.Environment, settings.PLAID_ENV, plaid.Environment.sandbox),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        self.api_client = ApiClient(self.configuration)
        self.client = plaid_api.PlaidApi(self.api_client)
    
    def create_link_token(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization"""
        try:
            request = LinkTokenCreateRequest(
                products=[getattr(Products, prod) for prod in settings.PLAID_PRODUCTS],
                client_name=settings.PROJECT_NAME,
                country_codes=[getattr(CountryCode, cc) for cc in settings.PLAID_COUNTRY_CODES],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )
            
            response = self.client.link_token_create(request)
            return {
                "link_token": response['link_token'],
                "expiration": response['expiration']
            }
        except Exception as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise Exception(f"Failed to create link token: {str(e)}")
    
    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """Exchange public token for access token"""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            
            return {
                "access_token": response['access_token'],
                "item_id": response['item_id']
            }
        except Exception as e:
            logger.error(f"Error exchanging public token: {str(e)}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch account information from Plaid"""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                accounts.append({
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "official_name": account.get('official_name'),
                    "type": account['type'],
                    "subtype": account['subtype'],
                    "mask": account.get('mask'),
                    "balances": {
                        "current": account['balances'].get('current'),
                        "available": account['balances'].get('available'),
                        "limit": account['balances'].get('limit')
                    }
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
            
            transactions = []
            for transaction in response['transactions']:
                transactions.append({
                    "transaction_id": transaction['transaction_id'],
                    "account_id": transaction['account_id'],
                    "amount": transaction['amount'],
                    "date": transaction['date'],
                    "name": transaction['name'],
                    "merchant_name": transaction.get('merchant_name'),
                    "category": transaction.get('category', []),
                    "category_id": transaction.get('category_id'),
                    "account_owner": transaction.get('account_owner'),
                    "pending": transaction.get('pending', False)
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