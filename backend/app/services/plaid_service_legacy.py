import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv

# Legacy Plaid client (2019-era)
# Installed via: plaid-python==5.0.0
from plaid import Client

logger = logging.getLogger(__name__)

# Load .env if present
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_PUBLIC_KEY = os.getenv("PLAID_PUBLIC_KEY")  # legacy key used by old Plaid Link
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")  # sandbox | development | production


def _get_client() -> Client:
    """Initialize the legacy Plaid client using public_key flow (2019)."""
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        logger.warning("PLAID_CLIENT_ID or PLAID_SECRET missing; Plaid calls will fail.")
    if not PLAID_PUBLIC_KEY:
        logger.warning("PLAID_PUBLIC_KEY missing; legacy Link may not initialize.")

    return Client(
        client_id=PLAID_CLIENT_ID,
        secret=PLAID_SECRET,
        public_key=PLAID_PUBLIC_KEY,
        environment=PLAID_ENV,
    )


def create_link_init_payload(products: Optional[List[str]] = None,
                              country_codes: Optional[List[str]] = None) -> Dict[str, Any]:
    """Return legacy Link init payload (front-end uses this to configure Plaid Link).

    Note: In 2019, Plaid Link was initialized with a public_key rather than a link_token.
    """
    prods = products or ["transactions"]
    countries = country_codes or ["US"]

    payload = {
        "public_key": PLAID_PUBLIC_KEY,
        "environment": PLAID_ENV,
        "products": prods,
        "country_codes": countries,
        "language": "en",
    }
    logger.info("Provided Plaid legacy link init payload (public_key flow)")
    return payload


def exchange_public_token(public_token: str) -> Dict[str, str]:
    """Exchange a public_token from Link for an access_token and item_id."""
    client = _get_client()
    resp = client.Item.public_token.exchange(public_token)
    return {
        "access_token": resp.get("access_token"),
        "item_id": resp.get("item_id"),
    }


def get_accounts(access_token: str) -> List[Dict[str, Any]]:
    """Fetch accounts for an access_token using the legacy client."""
    client = _get_client()
    resp = client.Accounts.get(access_token)
    accounts = resp.get("accounts", [])
    return accounts


def get_transactions(access_token: str, start_date: str, end_date: str,
                      account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Fetch transactions using legacy client.

    Dates must be YYYY-MM-DD.
    """
    client = _get_client()
    resp = client.Transactions.get(access_token, start_date, end_date, account_ids=account_ids)
    return resp
