# SmartBudget - Visual Architecture Diagrams

This document contains visual representations of the SmartBudget system architecture.

---

## System Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                        SMARTBUDGET SYSTEM                          │
│                     Personal Finance Tracker                       │
└───────────────────────────────────────────────────────────────────┘

┌────────────────┐           ┌──────────────────┐         ┌──────────┐
│   End Users    │           │   Mobile App     │         │ Backend  │
│  iOS/Android   │◄─────────►│  React Native    │◄───────►│ FastAPI  │
│   Expo Go      │           │   TypeScript     │         │  Python  │
└────────────────┘           └──────────────────┘         └─────┬────┘
                                      │                          │
                                      │                          │
                                      ▼                          ▼
                             ┌──────────────────┐     ┌──────────────┐
                             │  AsyncStorage    │     │ PostgreSQL   │
                             │  (Local Cache)   │     │  (Database)  │
                             └──────────────────┘     └──────────────┘
                                                              │
                                      ┌───────────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   Plaid API      │
                             │  (Banking Data)  │
                             └──────────────────┘
```

---

## Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                            │
│                         (Mobile Frontend)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Screens    │  │  Components  │  │  Navigation  │              │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤              │
│  │ HomeScreen   │  │ Financial    │  │ Bottom Tabs  │              │
│  │ Transactions │  │ Summary      │  │ Stack Nav    │              │
│  │ AddTrans     │  │ Investment   │  └──────────────┘              │
│  │ Account      │  │ Analysis     │                                │
│  └──────────────┘  │ PlaidConnect │                                │
│                     └──────────────┘                                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                    Services Layer                        │       │
│  ├─────────────────────────────────────────────────────────┤       │
│  │ authService   plaidLegacy   budgetData   investmentApi  │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                │ HTTP / REST API
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                              │
│                        (Backend API)                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                    API Routers                           │       │
│  ├─────────────────────────────────────────────────────────┤       │
│  │ auth.py   banks.py   plaid_legacy.py   insights.py     │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                  Business Services                       │       │
│  ├─────────────────────────────────────────────────────────┤       │
│  │ transaction_service   investment_service   parser       │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                    Core Infrastructure                   │       │
│  ├─────────────────────────────────────────────────────────┤       │
│  │ config.py   database.py   security.py                   │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                │ SQLAlchemy ORM
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
│                     (PostgreSQL Database)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  users   │  │bank_accounts │  │ transactions │  │ budgets  │  │
│  ├──────────┤  ├──────────────┤  ├──────────────┤  ├──────────┤  │
│  │ id       │  │ id           │  │ id           │  │ id       │  │
│  │ email    │  │ user_id  [FK]│  │ user_id  [FK]│  │ user_id  │  │
│  │ password │  │ plaid_id     │  │ account_id   │  │ category │  │
│  │ name     │  │ name         │  │ amount       │  │ amount   │  │
│  └──────────┘  │ balance      │  │ date         │  │ period   │  │
│                 └──────────────┘  │ merchant     │  └──────────┘  │
│                                    │ category     │                 │
│                                    └──────────────┘                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - User Authentication

```
┌─────────┐                                                    ┌──────────┐
│  User   │                                                    │ Database │
└────┬────┘                                                    └─────┬────┘
     │                                                                │
     │  1. Enter credentials                                          │
     ├──────────►┌───────────┐                                       │
     │           │ Login     │                                        │
     │           │ Screen    │                                        │
     │           └─────┬─────┘                                       │
     │                 │                                              │
     │                 │  2. POST /api/v1/auth/login                 │
     │                 ├────────────►┌──────────────┐                │
     │                 │             │  auth.py     │                │
     │                 │             │  (Router)    │                │
     │                 │             └──────┬───────┘                │
     │                 │                    │                         │
     │                 │                    │  3. Query user          │
     │                 │                    ├────────────────────────►│
     │                 │                    │                         │
     │                 │                    │  4. User record         │
     │                 │                    │◄────────────────────────┤
     │                 │                    │                         │
     │                 │                    │  5. Verify password     │
     │                 │                    ├─────────┐               │
     │                 │                    │         │               │
     │                 │                    │◄────────┘               │
     │                 │                    │                         │
     │                 │                    │  6. Generate JWT        │
     │                 │                    ├─────────┐               │
     │                 │                    │         │               │
     │                 │  7. Return token   │◄────────┘               │
     │                 │◄───────────────────┤                         │
     │                 │                    │                         │
     │                 │  8. Store token    │                         │
     │                 ├──────────┐         │                         │
     │                 │          │         │                         │
     │                 │◄─────────┘         │                         │
     │                 │                    │                         │
     │  9. Navigate to │                    │                         │
     │     Home screen │                    │                         │
     │◄────────────────┤                    │                         │
     │                 │                    │                         │
     │                 │  All future requests include:                │
     │                 │  Authorization: Bearer <JWT>                 │
     │                 │                    │                         │
```

---

## Data Flow - Plaid Bank Connection

```
┌──────┐  ┌────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐
│ User │  │ Mobile │  │ Backend │  │  Plaid  │  │ Database │
└──┬───┘  └───┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘
   │          │             │            │            │
   │  1. Click "Connect Bank"           │            │
   ├─────────►│             │            │            │
   │          │             │            │            │
   │          │  2. Request Link Token   │            │
   │          ├────────────►│            │            │
   │          │             │            │            │
   │          │             │  3. Create Link Token   │
   │          │             ├───────────►│            │
   │          │             │            │            │
   │          │             │  4. Link Token          │
   │          │             │◄───────────┤            │
   │          │             │            │            │
   │          │  5. Link Token            │            │
   │          │◄────────────┤            │            │
   │          │             │            │            │
   │          │  6. Open Plaid Link (Demo Modal)      │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │  7. Select Bank (Demo) │            │            │
   ├─────────►│             │            │            │
   │          │             │            │            │
   │  8. "Simulate Success" │            │            │
   ├─────────►│             │            │            │
   │          │             │            │            │
   │          │  9. Generate Mock Public Token        │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │          │  10. Exchange Token      │            │
   │          ├────────────►│            │            │
   │          │             │            │            │
   │          │             │  11. Exchange Public    │
   │          │             │      for Access Token   │
   │          │             ├───────────►│            │
   │          │             │            │            │
   │          │             │  12. Access Token       │
   │          │             │◄───────────┤            │
   │          │             │            │            │
   │          │             │  13. Save to DB         │
   │          │             ├───────────────────────►│
   │          │             │            │            │
   │          │  14. Access Token & Item ID          │
   │          │◄────────────┤            │            │
   │          │             │            │            │
   │          │  15. Store in AsyncStorage           │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │  16. Show Success       │            │            │
   │◄─────────┤             │            │            │
   │          │             │            │            │
```

---

## Data Flow - Transaction Sync

```
┌──────┐  ┌────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐
│ User │  │ Mobile │  │ Backend │  │  Plaid  │  │ Database │
└──┬───┘  └───┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘
   │          │             │            │            │
   │  1. Open Home Screen   │            │            │
   ├─────────►│             │            │            │
   │          │             │            │            │
   │          │  2. Load Dashboard Data  │            │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │          │  3. Check if connected   │            │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │          │  4. Fetch Transactions (last 30 days) │
   │          ├────────────►│            │            │
   │          │             │            │            │
   │          │             │  5. Get access_token    │
   │          │             ├───────────────────────►│
   │          │             │            │            │
   │          │             │  6. Access token        │
   │          │             │◄───────────────────────┤
   │          │             │            │            │
   │          │             │  7. Fetch transactions  │
   │          │             ├───────────►│            │
   │          │             │            │            │
   │          │             │  8. Transaction list    │
   │          │             │◄───────────┤            │
   │          │             │            │            │
   │          │  9. Return transactions  │            │
   │          │◄────────────┤            │            │
   │          │             │            │            │
   │          │  10. Categorize & Calculate           │
   │          ├────────┐    │            │            │
   │          │        │    │            │            │
   │          │  - Total Income          │            │
   │          │  - Total Expenses        │            │
   │          │  - By Category           │            │
   │          │        │    │            │            │
   │          │◄───────┘    │            │            │
   │          │             │            │            │
   │  11. Display Dashboard │            │            │
   │◄─────────┤             │            │            │
   │          │             │            │            │
   │  - Income: $5,200      │            │            │
   │  - Expenses: $3,450    │            │            │
   │  - Net: $1,750         │            │            │
   │          │             │            │            │
```

---

## Database Schema Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                             │
└─────────────────────────────────────────────────────────────────┘

    ┌────────────────────┐
    │      users         │
    ├────────────────────┤
    │ PK  id             │
    │     email          │
    │     hashed_password│
    │     full_name      │
    │     is_active      │
    │     created_at     │
    └──────────┬─────────┘
               │
               │  1:N
               │
    ┌──────────┴──────────────────────────────────────┐
    │                                                   │
    ▼                                                   ▼
┌───────────────────┐                        ┌─────────────────┐
│  bank_accounts    │                        │   budgets       │
├───────────────────┤                        ├─────────────────┤
│ PK  id            │                        │ PK  id          │
│ FK  user_id       │                        │ FK  user_id     │
│     plaid_account │                        │     category    │
│     plaid_item_id │                        │     amount      │
│     account_name  │                        │     period      │
│     account_type  │                        │     start_date  │
│     balance       │                        │     end_date    │
│     last_synced   │                        │     is_active   │
└──────────┬────────┘                        └─────────────────┘
           │
           │  1:N
           │
           ▼
┌──────────────────────┐
│    transactions      │
├──────────────────────┤
│ PK  id               │
│ FK  user_id          │
│ FK  account_id       │
│     plaid_trans_id   │
│     transaction_date │
│     amount           │
│     merchant_name    │
│     category         │
│     subcategory      │
│     description      │
│     is_pending       │
└──────────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  1:N = One-to-Many Relationship
```

---

## Component Hierarchy - Mobile App

```
App.tsx (Root)
│
└── NavigationContainer
    │
    └── Tab.Navigator (Bottom Tabs)
        │
        ├── Tab 1: Home
        │   │
        │   └── HomeScreen
        │       │
        │       ├── Header (Text: "SmartBudget")
        │       │
        │       ├── FinancialSummary
        │       │   ├── Connection Banner (if not connected)
        │       │   ├── Summary Cards (Income, Expenses, Net)
        │       │   ├── Income Table (by category)
        │       │   ├── Expenses Table (by category)
        │       │   └── Bar Chart (visualization)
        │       │
        │       └── InvestmentAnalysis
        │           ├── Risk Profile Display
        │           ├── Recommendations List
        │           ├── Savings Optimization Tips
        │           └── PortfolioUpload Component
        │
        ├── Tab 2: Transactions
        │   │
        │   └── TransactionsScreen
        │       ├── Filter Controls (date, category)
        │       ├── Transaction List (FlatList)
        │       │   └── TransactionItem (repeated)
        │       │       ├── Date
        │       │       ├── Merchant Name
        │       │       ├── Amount
        │       │       └── Category Badge
        │       └── Pull-to-Refresh
        │
        ├── Tab 3: Add
        │   │
        │   └── AddTransactionScreen
        │       ├── Form Header
        │       ├── Date Picker
        │       ├── Amount Input
        │       ├── Category Dropdown
        │       ├── Merchant Input
        │       ├── Notes TextArea
        │       └── Submit Button
        │
        └── Tab 4: Account
            │
            └── AccountScreen
                ├── User Profile Section
                ├── PlaidConnection Component
                │   ├── Connection Status
                │   ├── "Connect with Plaid" Button
                │   └── Demo Modal (when clicked)
                │       ├── Modal Header
                │       ├── Instructions
                │       └── "Simulate Success" Button
                ├── Connected Accounts List
                │   └── AccountItem (repeated)
                │       ├── Bank Name
                │       ├── Account Name
                │       ├── Balance
                │       └── Last Synced
                └── Settings Button
```

---

## API Router Organization

```
FastAPI Application (main.py)
│
├── Middleware
│   ├── CORS Middleware (allow mobile app)
│   └── Logging Middleware
│
├── Router: /api/plaid-legacy
│   ├── POST   /exchange-token
│   ├── GET    /accounts
│   ├── GET    /transactions
│   └── GET    /balance
│
├── Router: /api/v1/auth
│   ├── POST   /register
│   ├── POST   /login
│   ├── GET    /me
│   └── PUT    /me
│
├── Router: /api/v1/banks
│   ├── GET    /accounts
│   ├── GET    /accounts/{id}
│   ├── POST   /accounts
│   ├── PUT    /accounts/{id}
│   ├── DELETE /accounts/{id}
│   └── POST   /accounts/{id}/sync
│
└── Router: /api/v1/insights
    ├── GET    /recommendations
    ├── POST   /analyze
    ├── GET    /spending-analysis
    └── POST   /upload-portfolio

Each router connects to:
  ├── Business Services (services/)
  ├── Database Models (models/)
  └── Database Session (via dependency injection)
```

---

## Deployment Architecture

### Development Environment

```
┌──────────────────────────────────────────────┐
│         Local Developer Machine               │
├──────────────────────────────────────────────┤
│                                                │
│  Terminal 1:                                  │
│  ┌──────────────────────────────────┐        │
│  │  Backend (uvicorn)               │        │
│  │  http://localhost:8000           │        │
│  │  - FastAPI                       │        │
│  │  - Python 3.13                   │        │
│  │  - Virtual Environment           │        │
│  └──────────────────────────────────┘        │
│                                                │
│  Terminal 2:                                  │
│  ┌──────────────────────────────────┐        │
│  │  Mobile (Expo)                   │        │
│  │  http://localhost:8083           │        │
│  │  - React Native                  │        │
│  │  - Metro Bundler                 │        │
│  │  - Hot Reload                    │        │
│  └──────────────────────────────────┘        │
│                                                │
│  Database:                                    │
│  ┌──────────────────────────────────┐        │
│  │  PostgreSQL (Docker)             │        │
│  │  localhost:5432                  │        │
│  │  OR                              │        │
│  │  SQLite (budget_tracker.db)     │        │
│  └──────────────────────────────────┘        │
│                                                │
└──────────────────────────────────────────────┘
```

### Docker Compose Environment

```
┌────────────────────────────────────────────────┐
│            Docker Host                          │
├────────────────────────────────────────────────┤
│                                                  │
│  Container: postgres                            │
│  ┌────────────────────────────────────┐        │
│  │  PostgreSQL 16 Alpine              │        │
│  │  Port: 5432                        │        │
│  │  Volume: postgres_data             │        │
│  │  Health Check: pg_isready          │        │
│  └──────────────┬─────────────────────┘        │
│                 │                                │
│                 │  Network: bridge              │
│                 │                                │
│  Container: api ▼                               │
│  ┌────────────────────────────────────┐        │
│  │  FastAPI Application               │        │
│  │  Port: 8000                        │        │
│  │  Depends On: postgres              │        │
│  │  Env: APP_MODE=live                │        │
│  └────────────────────────────────────┘        │
│                 │                                │
└─────────────────┼────────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Mobile App (Host) │
         │  localhost:8000    │
         └────────────────────┘
```

### Production Cloud Architecture

```
┌───────────────────────────────────────────────────────┐
│                   Internet                             │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │   Load Balancer (HTTPS)│
         │   - SSL Termination    │
         │   - Health Checks      │
         │   - Auto-scaling       │
         └──────────┬─────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
┌───────────────┐        ┌───────────────┐
│ API Instance 1│        │ API Instance 2│
│ (Container)   │        │ (Container)   │
│ - FastAPI     │        │ - FastAPI     │
│ - Gunicorn    │        │ - Gunicorn    │
└───────┬───────┘        └───────┬───────┘
        │                        │
        └───────────┬────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Managed Database   │
         │  (AWS RDS / Azure)  │
         │  - PostgreSQL       │
         │  - Automated Backup │
         │  - Multi-AZ         │
         └─────────────────────┘

         ┌─────────────────────┐
         │  Object Storage     │
         │  (S3 / Azure Blob)  │
         │  - Document uploads │
         │  - Static assets    │
         └─────────────────────┘

         ┌─────────────────────┐
         │  Mobile Apps        │
         │  - iOS App Store    │
         │  - Google Play      │
         │  - https://api.url  │
         └─────────────────────┘
```

---

## Technology Stack Detail

```
┌─────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                      │
└─────────────────────────────────────────────────────────┘

FRONTEND (Mobile App)
├── Framework: React Native 0.74.5
├── Runtime: Expo ~51.0.28
├── Language: TypeScript 5.3.3
├── Navigation: React Navigation 6.x
│   ├── Bottom Tabs
│   └── Stack Navigator
├── State Management: React Hooks
│   ├── useState
│   ├── useEffect
│   └── useContext (future)
├── Storage: AsyncStorage 1.23.1
├── HTTP Client: Fetch API
└── UI Components: React Native Core

BACKEND (API Server)
├── Framework: FastAPI 0.115.0
├── Runtime: Python 3.13
├── Server: Uvicorn 0.30.6
├── ORM: SQLAlchemy 2.0.23
├── Validation: Pydantic 2.9.2
├── Authentication: 
│   ├── JWT (python-jose 3.3.0)
│   └── Password Hashing (passlib 1.7.4)
├── API Integration: Plaid Python 12.0.0
└── Document Parsing:
    ├── pandas 2.1.4
    ├── openpyxl 3.1.2
    └── beautifulsoup4 4.12.2

DATABASE
├── Production: PostgreSQL 16
├── Driver: psycopg2-binary 2.9.11
├── Development: SQLite 3
└── Migrations: SQLAlchemy (create_all)

INFRASTRUCTURE
├── Containerization: Docker
├── Orchestration: Docker Compose
├── Version Control: Git
├── CI/CD: GitHub Actions (planned)
└── Cloud: AWS/Azure (production)

EXTERNAL SERVICES
├── Banking Data: Plaid API
│   ├── Environment: Sandbox (dev)
│   └── Flow: Link Token → Public Token → Access Token
└── Future Integrations:
    ├── Email notifications
    ├── Push notifications
    └── SMS alerts
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                         │
└─────────────────────────────────────────────────────────┘

Layer 1: Transport Security
├── HTTPS/TLS (Production)
├── Certificate Pinning (future)
└── Secure WebSocket (future)

Layer 2: Authentication
├── JWT Tokens
│   ├── Algorithm: HS256
│   ├── Expiration: 30 minutes
│   └── Refresh Tokens (future)
├── Password Hashing: bcrypt
└── OAuth2 Flow (planned)

Layer 3: Authorization
├── User-scoped data queries
├── Role-based access control (future)
└── Resource ownership validation

Layer 4: Data Protection
├── Database:
│   ├── Encrypted connections (SSL)
│   ├── Encrypted sensitive fields
│   └── Regular backups
├── Storage:
│   ├── AsyncStorage (encrypted in production)
│   └── Secure Keychain (iOS future)
└── API:
    ├── Rate limiting (future)
    └── Input validation (Pydantic)

Layer 5: External Services
├── Plaid:
│   ├── Never store bank credentials
│   ├── Encrypted access tokens
│   └── Webhook signatures
└── Third-party APIs:
    ├── API key rotation
    └── Environment-based keys

Layer 6: Logging & Monitoring
├── Audit logs (future)
├── Error tracking
├── Security alerts
└── Anomaly detection (future)

Environment Variables (.env)
├── Never committed to git
├── Different values per environment
└── Secured in production (secrets manager)
```

---

**Last Updated**: December 2, 2025  
**Version**: 1.0

For more details, see:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture guide
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Developer onboarding
