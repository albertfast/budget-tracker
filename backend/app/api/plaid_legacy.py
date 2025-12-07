from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.services.plaid_service_legacy import (
    create_link_init_payload,
    exchange_public_token as legacy_exchange_public_token,
    get_accounts as legacy_get_accounts,
    get_transactions as legacy_get_transactions,
)

router = APIRouter(prefix="/plaid-legacy", tags=["plaid-legacy"])


class PublicTokenPayload(BaseModel):
    public_token: str


@router.get("/link-init")
def link_init(products: Optional[str] = Query(None), country_codes: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Legacy (2019) Link init endpoint returning public_key config.

    products: comma-separated list (e.g., "transactions,auth")
    country_codes: comma-separated list (default US)
    """
    try:
        prods: Optional[List[str]] = products.split(",") if products else None
        countries: Optional[List[str]] = country_codes.split(",") if country_codes else None
        return create_link_init_payload(products=prods, country_codes=countries)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to build link init payload: {e}")


@router.post("/exchange-token")
def exchange_public_token(payload: PublicTokenPayload) -> Dict[str, str]:
    """Exchange public_token for access_token (legacy flow)."""
    try:
        return legacy_exchange_public_token(payload.public_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Exchange failed: {e}")


@router.get("/accounts")
def get_accounts(access_token: str = Query(...)) -> Dict[str, Any]:
    """Return accounts for an access_token."""
    try:
        accounts = legacy_get_accounts(access_token)
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Accounts fetch failed: {e}")


@router.get("/transactions")
def get_transactions(
    access_token: str = Query(...),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
) -> Dict[str, Any]:
    """Return transactions for an access_token and date range (legacy client)."""
    try:
        acct_ids: Optional[List[str]] = account_ids.split(",") if account_ids else None
        resp = legacy_get_transactions(access_token, start_date, end_date, account_ids=acct_ids)
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transactions fetch failed: {e}")
