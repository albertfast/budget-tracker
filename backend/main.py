from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Environment variables
load_dotenv()

app = FastAPI(
    title="SmartBudget API",
    description="Backend API for SmartBudget mobile application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plaid configuration
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "68f9e88c17270900222dae83")
PLAID_SECRET = os.getenv("PLAID_SECRET", "ce8fb384dc57b556987e6874f719d9")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox").lower()
PLAID_COUNTRY_CODES = ["US"]
PLAID_PRODUCTS = ["transactions"]

# Plaid environment URLs
PLAID_BASE_URLS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com"
}

PLAID_BASE_URL = PLAID_BASE_URLS.get(PLAID_ENV, PLAID_BASE_URLS["sandbox"])

# Request models
class LinkTokenRequest(BaseModel):
    user: Dict[str, str]
    products: Optional[list] = PLAID_PRODUCTS
    country_codes: Optional[list] = PLAID_COUNTRY_CODES
    language: Optional[str] = "en"
    webhook: Optional[str] = None

class PublicTokenRequest(BaseModel):
    public_token: str

class AccessTokenRequest(BaseModel):
    access_token: str

class TransactionsRequest(BaseModel):
    access_token: str
    start_date: str
    end_date: str


class SandboxPublicTokenRequest(BaseModel):
    """Request model for creating a Plaid Sandbox public token.

    The client will typically send the Supabase email and the password
    used for logging into the app. For Plaid Sandbox we must send only
    the username part (before the `@`) as `override_username`, otherwise
    credentials like `user_good@good` will not be accepted. The password
    can be forwarded as-is (for example `pass_good`).
    """

    email: str
    password: str
    institution_id: Optional[str] = "ins_109508"
    custom_user_config: Optional[Dict[str, Any]] = None


class SandboxCustomUserRequest(BaseModel):
    """Request model for creating a custom Plaid Sandbox user with specific data.
    
    This allows you to create test users with custom accounts, transactions,
    holdings, and other financial data for testing purposes.
    """
    
    username: str
    password: str = "pass_good"
    institution_id: str = "ins_109508"
    config: Dict[str, Any]  # The custom user configuration JSON


def _plaid_username_from_email(email: str) -> str:
    """Return the part of the email before the `@`.

    Plaid Sandbox expects usernames like `user_good`. When the user logs
    into the mobile app with an email such as `user_good@good`, we must
    strip everything after `@` before sending it as `override_username`.
    """

    if not email:
        return ""

    # Split once on '@' and take the local-part.
    return email.split("@", 1)[0]

@app.get("/")
async def root():
    return {"message": "SmartBudget API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/create_link_token")
def create_link_token(user_email: str):
    body = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "user": {
            "client_user_id": user_email
        },
        "client_name": "Budget Tracker",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
        "webhook": "https://example.com/webhook"
    }
    response = requests.post(f"{PLAID_BASE_URL}/link/token/create", json=body)
    return response.json()


@app.post("/api/plaid/sandbox/public_token")
def create_sandbox_public_token(request: SandboxPublicTokenRequest):
    """Programmatically create a Sandbox public_token using test credentials.

    This mirrors the manual cURL call to `/sandbox/public_token/create` but
    ensures that, when the user logged in via Supabase with an email like
    `user_good@good`, Plaid receives `override_username = "user_good"`.
    """

    plaid_username = _plaid_username_from_email(request.email)

    body: Dict[str, Any] = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "institution_id": request.institution_id,
        "initial_products": ["transactions"],
        "options": {
            "webhook": "https://www.genericwebhookurl.com/webhook",
            "override_username": plaid_username,
            "override_password": request.password,
        },
    }
    
    # Add custom user config if provided
    if request.custom_user_config:
        body["options"]["override_accounts"] = request.custom_user_config.get("override_accounts", [])
        if "seed" in request.custom_user_config:
            body["options"]["seed"] = request.custom_user_config["seed"]

    response = requests.post(f"{PLAID_BASE_URL}/sandbox/public_token/create", json=body)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Plaid sandbox error: {response.text}",
        )

    return response.json()


@app.post("/api/plaid/sandbox/custom_user")
def create_custom_sandbox_user(request: SandboxCustomUserRequest):
    """Create a custom Plaid Sandbox user with specific financial data.
    
    This endpoint uses Plaid's user_custom feature to create test users with:
    - Custom accounts (checking, savings, credit, loan, investment, payroll)
    - Custom transactions with specific dates and amounts  
    - Custom holdings and investment transactions
    - Custom identity data
    
    The username should be "user_custom" and you provide the config in user_json.
    """
    
    # For custom users, username must be "user_custom" and config goes in user_json
    body: Dict[str, Any] = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "institution_id": request.institution_id,
        "initial_products": ["transactions"],
        "options": {
            "webhook": "https://www.genericwebhookurl.com/webhook",
            "override_username": "user_custom",
            "override_password": request.password,
            "user_json": request.config  # Custom config goes here
        },
    }
    
    response = requests.post(f"{PLAID_BASE_URL}/sandbox/public_token/create", json=body)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Plaid sandbox error: {response.text}",
        )
    
    result = response.json()
    
    # Return with additional info
    result["username"] = "user_custom"
    result["config_applied"] = True
    
    return result

# Plaid endpoints
@app.post("/api/banks/link/create-token")
async def create_plaid_link_token(request: LinkTokenRequest):
    try:
        payload = {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "user": request.user,
            "client_name": "SmartBudget App",
            "products": request.products,
            "country_codes": request.country_codes,
            "language": request.language
        }
        
        if request.webhook:
            payload["webhook"] = request.webhook
            
        response = requests.post(
            f"{PLAID_BASE_URL}/link/token/create",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plaid API error: {response.text}"
            )
            
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plaid/exchange-token")
async def exchange_public_token(request: PublicTokenRequest):
    try:
        payload = {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "public_token": request.public_token
        }
        
        response = requests.post(
            f"{PLAID_BASE_URL}/item/public_token/exchange",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plaid API error: {response.text}"
            )
            
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plaid/accounts")
async def get_accounts(request: AccessTokenRequest):
    try:
        payload = {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "access_token": request.access_token
        }
        
        response = requests.post(
            f"{PLAID_BASE_URL}/accounts/get",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plaid API error: {response.text}"
            )
            
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plaid/transactions")
async def get_transactions(request: TransactionsRequest):
    try:
        payload = {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "access_token": request.access_token,
            "start_date": request.start_date,
            "end_date": request.end_date
        }
        
        response = requests.post(
            f"{PLAID_BASE_URL}/transactions/get",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plaid API error: {response.text}"
            )
            
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints for compatibility
@app.get("/api/accounts")
async def get_accounts():
    return {"accounts": []}

@app.get("/api/transactions")
async def get_transactions():
    return {"transactions": []}

@app.post("/api/plaid/create_link_token")
async def create_plaid_link_token_legacy():
    return {"link_token": "placeholder"}

@app.post("/api/plaid/webhook")
async def plaid_webhook(request: dict):
    try:
        webhook_type = request.get("webhook_type")
        webhook_code = request.get("webhook_code")
        
        print(f"[Plaid Webhook] Type: {webhook_type}, Code: {webhook_code}")
        
        # Handle different webhook types
        if webhook_type == "TRANSACTIONS":
            # Handle new transactions
            item_id = request.get("item_id")
            new_transactions = request.get("new_transactions", [])
            print(f"[Plaid Webhook] {len(new_transactions)} new transactions for item {item_id}")
            
        elif webhook_type == "ITEM":
            # Handle item updates
            item_id = request.get("item_id")
            webhook_code = request.get("webhook_code")
            print(f"[Plaid Webhook] Item {item_id} update: {webhook_code}")
            
        return {"status": "received"}
        
    except Exception as e:
        print(f"[Plaid Webhook] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plaid/sync_transactions")
def sync_transactions(request: AccessTokenRequest):
    """Fetch transactions from Plaid for a given access token.
    
    Returns all transactions with details like amount, description, category, etc.
    This data can then be stored in Supabase and used for AI analysis.
    """
    try:
        # Get transactions for the last 30 days
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        payload = {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "access_token": request.access_token,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(
            f"{PLAID_BASE_URL}/transactions/get",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Plaid API error: {response.text}"
            )
        
        data = response.json()
        
        return {
            "transactions": data.get("transactions", []),
            "accounts": data.get("accounts", []),
            "total_transactions": data.get("total_transactions", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AnalyzeSpendingRequest(BaseModel):
    transactions: list


@app.post("/api/ai/analyze_spending")
def analyze_spending(request: AnalyzeSpendingRequest):
    """AI-powered spending analysis.
    
    Analyzes transaction patterns and provides:
    - Category breakdown
    - Spending trends
    - Savings recommendations
    - Budget suggestions
    """
    try:
        transactions = request.transactions
        
        if not transactions:
            return {
                "summary": "No transactions to analyze",
                "recommendations": []
            }
        
        # Calculate spending by category
        category_totals = {}
        total_spending = 0
        
        for tx in transactions:
            amount = abs(tx.get("amount", 0))
            category = tx.get("category", ["Uncategorized"])[0] if tx.get("category") else "Uncategorized"
            
            if amount > 0:  # Only count debits (spending)
                category_totals[category] = category_totals.get(category, 0) + amount
                total_spending += amount
        
        # Generate recommendations
        recommendations = []
        
        # Find top spending categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_categories:
            top_category, top_amount = sorted_categories[0]
            percentage = (top_amount / total_spending * 100) if total_spending > 0 else 0
            
            if percentage > 40:
                recommendations.append({
                    "type": "warning",
                    "category": top_category,
                    "message": f"Your {top_category} spending represents {percentage:.1f}% of your total expenses. Consider reducing spending in this category.",
                    "potential_savings": top_amount * 0.2  # 20% savings potential
                })
        
        # Check for subscription-like recurring charges
        recurring_charges = {}
        for tx in transactions:
            desc = tx.get("name", "").lower()
            amount = abs(tx.get("amount", 0))
            
            if any(keyword in desc for keyword in ["subscription", "netflix", "spotify", "monthly", "annual"]):
                recurring_charges[desc] = recurring_charges.get(desc, 0) + amount
        
        if recurring_charges:
            total_subscriptions = sum(recurring_charges.values())
            recommendations.append({
                "type": "info",
                "category": "Subscriptions",
                "message": f"Your subscription costs: ${total_subscriptions:.2f}. Consider canceling unused subscriptions.",
                "potential_savings": total_subscriptions * 0.3
            })
        
        return {
            "total_spending": total_spending,
            "category_breakdown": category_totals,
            "top_categories": sorted_categories[:5],
            "recommendations": recommendations,
            "analysis_period": "Last 30 days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/investment_advice")
def investment_advice(request: dict):
    """AI-powered investment recommendations.
    
    Based on user's income, expenses, and risk profile, provides:
    - Investment allocation suggestions
    - Risk-adjusted portfolio recommendations
    - Savings goals
    """
    try:
        monthly_income = request.get("monthly_income", 0)
        monthly_expenses = request.get("monthly_expenses", 0)
        current_savings = request.get("current_savings", 0)
        risk_profile = request.get("risk_profile", "moderate")  # conservative, moderate, aggressive
        
        disposable_income = monthly_income - monthly_expenses
        
        if disposable_income <= 0:
            return {
                "message": "You need to optimize your income and expense balance",
                "recommendations": [{
                    "type": "warning",
                    "message": "Focus on reducing your expenses first"
                }]
            }
        
        # Calculate recommended allocations
        recommendations = []
        
        # Emergency fund first
        emergency_fund_target = monthly_expenses * 6
        emergency_fund_needed = max(0, emergency_fund_target - current_savings)
        
        if emergency_fund_needed > 0:
            recommendations.append({
                "type": "priority",
                "category": "Emergency Fund",
                "message": f"First, build an emergency fund of ${emergency_fund_needed:.2f}",
                "monthly_contribution": min(disposable_income * 0.3, emergency_fund_needed / 6),
                "timeframe": "6-12 months"
            })
        
        # Investment allocation based on risk profile
        remaining_income = disposable_income * 0.7  # After emergency fund
        
        if risk_profile == "conservative":
            allocation = {
                "bonds": 0.6,
                "stocks": 0.3,
                "cash": 0.1
            }
        elif risk_profile == "aggressive":
            allocation = {
                "stocks": 0.7,
                "bonds": 0.2,
                "alternative": 0.1
            }
        else:  # moderate
            allocation = {
                "stocks": 0.5,
                "bonds": 0.4,
                "cash": 0.1
            }
        
        for asset_class, percentage in allocation.items():
            amount = remaining_income * percentage
            recommendations.append({
                "type": "investment",
                "category": asset_class.title(),
                "message": f"Invest ${amount:.2f} monthly in {asset_class.title()}",
                "percentage": percentage * 100,
                "monthly_amount": amount
            })
        
        return {
            "disposable_income": disposable_income,
            "recommended_monthly_investment": remaining_income,
            "risk_profile": risk_profile,
            "allocation": allocation,
            "recommendations": recommendations,
            "projected_annual_savings": remaining_income * 12
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plaid/webhook")
async def plaid_webhook(request: dict):
    try:
        webhook_type = request.get("webhook_type")
        webhook_code = request.get("webhook_code")
        
        print(f"[Plaid Webhook] Type: {webhook_type}, Code: {webhook_code}")
        
        # Handle different webhook types
        if webhook_type == "TRANSACTIONS":
            # Handle new transactions
            item_id = request.get("item_id")
            new_transactions = request.get("new_transactions", [])
            print(f"[Plaid Webhook] {len(new_transactions)} new transactions for item {item_id}")
            
        elif webhook_type == "ITEM":
            # Handle item updates
            item_id = request.get("item_id")
            webhook_code = request.get("webhook_code")
            print(f"[Plaid Webhook] Item {item_id} update: {webhook_code}")
            
        return {"status": "received"}
        
    except Exception as e:
        print(f"[Plaid Webhook] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)