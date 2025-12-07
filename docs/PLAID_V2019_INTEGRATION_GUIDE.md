# Plaid API v2019 Integration Guide

## Overview

SmartBudget now includes full Plaid API (2019 version) integration for user login and financial data synchronization. Users can connect their bank accounts and automatically sync income/expense data to the dashboard.

**Key Features:**
- ✅ Plaid Link login (v2019 legacy - public_key flow)
- ✅ Multi-bank account support
- ✅ Automatic transaction sync
- ✅ Income/expense categorization
- ✅ Dashboard data integration
- ✅ Secure token storage
- ✅ Refresh/resync capability

---

## Architecture

### Backend Components

#### 1. **Plaid Auth Service** (`backend/app/services/plaid_auth_service.py`)

Core service handling Plaid operations:

```python
# Authentication & Login Flow
create_plaid_link_session(user_id, db) -> str
complete_plaid_login(user_id, public_token, db) -> Dict

# Data Synchronization
sync_plaid_transactions(user_id, access_token, db) -> Dict
refresh_plaid_tokens(user_id, db) -> Dict

# Dashboard Integration
get_user_financial_summary(user_id, db, days=30) -> Dict
```

**Workflow:**
```
User Login → Create Plaid Link Session → Connect via Plaid Link →
Exchange public_token → Store access_token & accounts →
Sync transactions → Categorize as income/expense →
Update dashboard
```

#### 2. **Authentication API Endpoints** (`backend/app/api/auth.py`)

New Plaid-specific endpoints:

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------  |
| `/auth/plaid/link-init` | POST | ✅ Yes | Initialize Plaid Link for user |
| `/auth/plaid/complete-login` | POST | ✅ Yes | Complete Plaid login flow |
| `/financial-summary` | GET | ✅ Yes | Get income/expense dashboard data |
| `/plaid/refresh` | POST | ✅ Yes | Manually refresh synced data |

#### 3. **Database Models**

**PlaidLinkSession:**
```python
- id: UUID (primary key)
- user_id: FK(User)
- link_token: String
- public_token: String (temporary)
- access_token: String (permanent)
- item_id: String (Plaid identifier)
- status: String (created | linked | expired | error)
- created_at: DateTime
- completed_at: DateTime
- expires_at: DateTime
```

**BankAccount:**
```python
- id: UUID
- user_id: FK(User)
- plaid_access_token: String (encrypted in production)
- plaid_item_id: String
- plaid_account_id: String
- account_name: String (user-friendly)
- bank_name: String
- account_type: String (checking, savings, credit, etc.)
- mask: String (last 4 digits)
- current_balance: Float
- available_balance: Float
- is_active: Boolean
- last_synced_at: DateTime
```

**Transaction:**
```python
- id: UUID
- bank_account_id: FK(BankAccount)
- plaid_transaction_id: String (unique)
- amount: Float (positive=credit, negative=debit)
- description: String
- date: DateTime
- category_primary: String (Income | Expense)
- category_detailed: String
- merchant_name: String
- is_pending: Boolean
- is_manual: Boolean
- created_at: DateTime
```

---

### Frontend Components

#### 1. **ConnectAccountScreen.tsx**

Mobile screen for Plaid Link integration:

```typescript
// Plaid Link initialization
handleInitPlaidLink()

// Connection success handler
handlePlaidSuccess(publicToken, metadata)
  → Calls /auth/plaid/complete-login
  → Stores user_id in AsyncStorage
  → Displays connected accounts & synced transactions

// Fetch accounts & transactions
fetchAccounts() → Calls /api/plaid-legacy/accounts
fetchTransactions() → Calls /api/plaid-legacy/transactions

// Disconnect handler
handleDisconnect()
```

#### 2. **PlaidConnection Component**

Wrapper for Plaid Link:

```typescript
import PlaidConnection from '@/components/PlaidConnection'

<PlaidConnection
  onSuccess={(publicToken, metadata) => handlePlaidSuccess(publicToken, metadata)}
  onExit={(error) => handlePlaidExit(error)}
/>
```

---

## Flow Diagrams

### User Login with Plaid

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User navigates to ConnectAccountScreen                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. App calls /auth/plaid/link-init (authenticated)         │
│    → Returns public_key + config for Plaid Link             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PlaidConnection component initializes Plaid Link         │
│    User selects bank & logs in with credentials             │
│    Plaid returns public_token                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. App calls /auth/plaid/complete-login with public_token  │
│    ✓ Authenticated request (requires valid JWT)             │
│    ✓ User must match authenticated user_id                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Backend completes Plaid login:                           │
│    a) Exchanges public_token → access_token                │
│    b) Fetches user's bank accounts from Plaid               │
│    c) Stores accounts in BankAccount table                 │
│    d) Syncs last 90 days of transactions                   │
│    e) Categorizes as Income/Expense                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Backend returns success response with:                   │
│    - access_token (for dashboard)                          │
│    - item_id (Plaid identifier)                            │
│    - accounts list with balances                           │
│    - transactions_synced count                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Mobile app displays success with account details         │
│    Dashboard auto-updates with synced transactions          │
└─────────────────────────────────────────────────────────────┘
```

### Transaction Sync & Dashboard Update

```
┌─────────────────────────────────────────────────────────────┐
│ Plaid API                                                   │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ sync_plaid_transactions()                                   │
│ - Fetch transactions (last 90 days)                         │
│ - For each transaction:                                     │
│   * Check if plaid_transaction_id already in DB             │
│   * Categorize (income/expense keyword matching)            │
│   * Create Transaction record                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ Transaction Table                                           │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ ID  │ Description │ Amount │ Category │ Date       │    │
│ ├─────┼─────────────┼────────┼──────────┼────────────┤    │
│ │ 1   │ SALARY 2024 │ +3500  │ Income   │ 2024-12-01 │    │
│ │ 2   │ GROCERY     │ -125   │ Expense  │ 2024-12-02 │    │
│ │ 3   │ BONUS       │ +500   │ Income   │ 2024-12-05 │    │
│ │ ... │ ...         │ ...    │ ...      │ ...        │    │
│ └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ get_user_financial_summary()                                │
│ - Query transactions (last 30 days)                         │
│ - Calculate totals by category                              │
│ - Group income vs expenses                                  │
│ - Return structured summary                                 │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ Dashboard (HomeScreen)                                      │
│ ┌───────────────────────────┐                               │
│ │ Income:  +$4,000 (2 trans)│                               │
│ │ Expenses: -$200 (5 trans) │                               │
│ │ Net:     +$3,800          │                               │
│ └───────────────────────────┘                               │
│ [FinancialSummary Component]                                │
│ - Bar chart by category                                     │
│ - Recent transactions list                                  │
│ - Breakdown by merchant                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Reference

### 1. Initialize Plaid Link

```http
POST /api/auth/plaid/link-init
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "session_id": "uuid",
  "public_key": "public_key_xxx",
  "environment": "sandbox",
  "products": ["transactions"],
  "country_codes": ["US"]
}
```

### 2. Complete Plaid Login

```http
POST /api/auth/plaid/complete-login
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "user_id": "uuid",
  "public_token": "public_xxx_abc"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "access_token": "access_xxx",
  "item_id": "item_xxx",
  "accounts_count": 2,
  "transactions_synced": 145,
  "accounts": [
    {
      "id": "uuid",
      "name": "Checking Account",
      "type": "checking",
      "mask": "1234",
      "balance": 5234.50,
      "available": 5000.00
    },
    {
      "id": "uuid",
      "name": "Savings Account",
      "type": "savings",
      "mask": "5678",
      "balance": 10500.00,
      "available": 10500.00
    }
  ]
}
```

### 3. Get Financial Summary

```http
GET /api/auth/financial-summary?days=30
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "period_days": 30,
  "start_date": "2024-11-06",
  "end_date": "2024-12-06",
  "total_transactions": 47,
  "income_total": 4500.00,
  "expense_total": 1250.75,
  "net_income": 3249.25,
  "by_category": {
    "Income": {
      "count": 2,
      "total": 4500.00,
      "average": 2250.00
    },
    "Expense": {
      "count": 45,
      "total": 1250.75,
      "average": 27.79
    }
  },
  "transactions": [
    {
      "id": "uuid",
      "description": "AMAZON PURCHASE",
      "amount": -45.99,
      "category": "Expense",
      "date": "2024-12-06T14:30:00"
    },
    {
      "id": "uuid",
      "description": "SALARY DEPOSIT",
      "amount": 3500.00,
      "category": "Income",
      "date": "2024-12-01T09:00:00"
    }
  ]
}
```

### 4. Refresh Plaid Data

```http
POST /api/auth/plaid/refresh
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "sync_result": {
    "total_synced": 23,
    "income_count": 2,
    "expense_count": 21,
    "date_range": "2024-09-06 to 2024-12-06"
  },
  "last_synced": "2024-12-06T15:45:30"
}
```

---

## Environment Configuration

### Backend (.env)

```bash
# Plaid Configuration
PLAID_CLIENT_ID=your_client_id_xxx
PLAID_SECRET=your_secret_xxx
PLAID_PUBLIC_KEY=your_public_key_xxx
PLAID_ENV=sandbox  # sandbox | development | production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smartbudget

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Mobile

No additional environment variables needed. The app automatically:
- Detects backend at `http://localhost:8000`
- Stores JWT token in AsyncStorage
- Stores user_id in AsyncStorage

---

## Security Implementation

### Backend Authentication

**All Plaid endpoints require valid JWT token:**

```python
# Example: complete_plaid_login endpoint
@router.post("/plaid/complete-login")
async def complete_plaid_login_endpoint(
    request: PlaidCompleteLoginRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # 1. Verify JWT token
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    
    # 2. Extract user_id from token
    user_id = payload.get("sub")
    
    # 3. Verify request user_id matches authenticated user
    if request.user_id != user_id:
        raise HTTPException(403, "Cannot complete login for different user")
    
    # 4. Only then complete Plaid login
    result = complete_plaid_login(user_id, request.public_token, db)
```

### Token Security

- ✅ All tokens stored in AsyncStorage (mobile) / database (backend)
- ✅ JWT tokens expire after 30 minutes (configurable)
- ✅ Plaid access_tokens encrypted in production
- ✅ No sensitive data returned in API responses
- ✅ HTTPS required in production

---

## Transaction Categorization Logic

Transactions are automatically categorized as **Income** or **Expense**:

### Income Keywords (Positive Match)
```
- salary
- paycheck
- deposit
- transfer
- refund
- bonus
- income
```

### Expense Logic
- If amount < 0: **Expense**
- If amount > 0 and no income keyword: **Income** (default)

### Example Categorization

| Description | Amount | Category | Logic |
|-------------|--------|----------|-------|
| SALARY DEPOSIT | +3500 | Income | Contains "salary" |
| WALMART PURCHASE | -45.99 | Expense | Negative amount |
| AMAZON RETURN | +25.00 | Income | Positive, no keyword |
| ATM WITHDRAWAL | -200.00 | Expense | Negative amount |
| BONUS PAYMENT | +500.00 | Income | Contains "bonus" |

---

## Testing

### Sandbox Environment

Plaid provides test credentials for sandbox:

```
Bank: Sandbox Bank
Username: user_good
Password: pass_good
```

### Test Workflow

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd mobile
   npm start
   ```

3. **Register & Login:**
   - Create account
   - Log in with valid credentials

4. **Connect Bank:**
   - Navigate to "Connect Account" screen
   - Click "Connect with Plaid"
   - Use sandbox credentials (user_good / pass_good)
   - Verify success message

5. **Check Dashboard:**
   - Navigate to Home screen
   - Should see FinancialSummary with synced data
   - Should see Income/Expense breakdown
   - Should see recent transactions

6. **Verify Database:**
   ```sql
   -- Check bank accounts
   SELECT * FROM bank_accounts WHERE user_id = 'your_user_id';
   
   -- Check transactions
   SELECT COUNT(*), category_primary, SUM(amount)
   FROM transactions
   GROUP BY category_primary;
   ```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid public_key"
- **Cause:** PLAID_PUBLIC_KEY not set in .env
- **Fix:** Check backend/.env has PLAID_PUBLIC_KEY value
- **Verify:** `echo $PLAID_PUBLIC_KEY` in terminal

#### 2. "Failed to complete Plaid login"
- **Cause:** User not authenticated or missing user_id
- **Fix:** Ensure user is logged in before connecting bank
- **Debug:** Check AsyncStorage for authToken

#### 3. "No transactions synced"
- **Cause:** Transactions already in database (duplicate plaid_transaction_id)
- **Fix:** Check database for existing transactions
- **Reset:** Delete old transactions from DB to re-sync

#### 4. "Bank not showing in Plaid Link"
- **Cause:** Bank not supported in current country/environment
- **Fix:** Change PLAID_ENV to "development" for more banks
- **Note:** Sandbox has limited bank options

### Debug Logging

Enable detailed logging:

```python
# backend/app/services/plaid_auth_service.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Check logs for:
# - "Successfully exchanged public_token"
# - "Stored N bank accounts"
# - "Synced N transactions"
```

---

## Future Enhancements

### Planned Features

1. **Real-time Updates**
   - Webhook notifications from Plaid
   - Automatic transaction refresh
   - Balance change alerts

2. **Advanced Categorization**
   - ML-based categorization
   - User custom categories
   - Recurring transaction detection

3. **Multi-currency Support**
   - Support for international banks
   - Currency conversion
   - Multi-currency dashboard

4. **Data Export**
   - CSV export of transactions
   - PDF reports
   - Tax category support

5. **Budget Integration**
   - Auto-create budgets from spending
   - Budget alerts
   - Spending forecasts

---

## References

- [Plaid API Documentation](https://plaid.com/docs/)
- [Plaid Python SDK (v5)](https://github.com/plaid/plaid-python)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

## Support & Questions

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `backend/app/services/plaid_auth_service.py`
3. Check mobile console: `npm start` output
4. Verify database: `psql -d smartbudget -c "SELECT * FROM bank_accounts;"`

