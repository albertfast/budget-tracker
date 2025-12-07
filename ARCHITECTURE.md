# SmartBudget Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Layers](#architecture-layers)
4. [Data Flow](#data-flow)
5. [Component Interactions](#component-interactions)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Authentication & Security](#authentication--security)
9. [External Integrations](#external-integrations)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

SmartBudget is a full-stack personal finance tracking application with three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                      SMARTBUDGET SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐      ┌─────────────────┐      ┌───────┐ │
│  │  Mobile App    │◄────►│   Backend API   │◄────►│  DB   │ │
│  │  (React Native)│      │    (FastAPI)    │      │ (PG)  │ │
│  └────────────────┘      └─────────────────┘      └───────┘ │
│         │                         │                           │
│         │                         │                           │
│         └─────────┬───────────────┘                           │
│                   ▼                                           │
│            ┌─────────────┐                                    │
│            │ Plaid API   │                                    │
│            │ (Banking)   │                                    │
│            └─────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

### Design Philosophy
- **Mobile-First**: React Native for cross-platform mobile experience
- **API-Driven**: RESTful backend with clear separation of concerns
- **Data Security**: Encrypted storage, secure token handling, PostgreSQL for production
- **Modular**: Loosely coupled components for maintainability
- **Dual-Mode**: Supports both offline (SQLite) and live (PostgreSQL) modes

---

## Technology Stack

### Frontend (`mobile/`)
```
├── Framework: React Native (Expo)
├── Language: TypeScript
├── State Management: React Hooks (useState, useEffect)
├── Navigation: React Navigation (Bottom Tabs)
├── Storage: AsyncStorage (development)
├── HTTP Client: Fetch API with custom auth service
└── UI Components: React Native core components
```

**Key Dependencies:**
- `expo`: ~51.0.28
- `react-native`: 0.74.5
- `@react-navigation/native`: ^6.1.18
- `@react-navigation/bottom-tabs`: ^6.6.1
- `@react-native-async-storage/async-storage`: 1.23.1

### Backend (`backend/`)
```
├── Framework: FastAPI
├── Language: Python 3.13
├── ORM: SQLAlchemy 2.0
├── Database: PostgreSQL (production) / SQLite (development)
├── Authentication: JWT (python-jose)
├── API Integration: Plaid (banking data)
└── Document Parsing: pandas, openpyxl, BeautifulSoup4
```

**Key Dependencies:**
- `fastapi`: 0.115.0
- `uvicorn[standard]`: 0.30.6
- `sqlalchemy`: 2.0.23
- `psycopg2-binary`: 2.9.11
- `plaid-python`: 12.0.0
- `pydantic`: 2.9.2

### Infrastructure (`infra/`)
```
├── Containerization: Docker & Docker Compose
├── Database: PostgreSQL 16 Alpine
└── Orchestration: docker-compose.yml
```

---

## Architecture Layers

### 1. Presentation Layer (Mobile App)

```
mobile/
├── App.tsx                          # Entry point, navigation setup
├── src/
│   ├── screens/                     # UI screens (pages)
│   │   ├── HomeScreen.tsx          # Dashboard with summaries
│   │   ├── TransactionsScreen.tsx  # Transaction list/filters
│   │   ├── AddTransactionScreen.tsx # Manual entry form
│   │   └── AccountScreen.tsx       # Account management & Plaid
│   ├── components/                  # Reusable UI components
│   │   ├── FinancialSummary.tsx    # Income/expense dashboard
│   │   ├── InvestmentAnalysis.tsx  # Investment insights
│   │   ├── PlaidConnection.tsx     # Plaid link handler
│   │   └── PortfolioUpload.tsx     # Document upload
│   ├── services/                    # Business logic & API calls
│   │   ├── authService.ts          # Authentication utilities
│   │   ├── plaidLegacy.ts          # Plaid API integration
│   │   ├── budgetData.ts           # Budget calculations
│   │   └── investmentApi.ts        # Investment endpoints
│   ├── navigation/                  # App navigation structure
│   │   └── BottomTabs.tsx          # Bottom tab navigator
│   └── types/                       # TypeScript type definitions
│       └── index.ts                # Shared types
```

**Responsibilities:**
- User interface rendering
- User input handling
- Client-side validation
- State management
- API communication
- Local data caching (AsyncStorage)

### 2. Application Layer (Backend API)

```
backend/
├── app/
│   ├── main.py                     # FastAPI app initialization
│   ├── api/                        # API route handlers
│   │   ├── auth.py                # User authentication endpoints
│   │   ├── banks.py               # Bank account CRUD (DB-backed)
│   │   ├── plaid_legacy.py        # Plaid proxy endpoints
│   │   └── insights.py            # Financial analysis endpoints
│   ├── core/                       # Core infrastructure
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection & sessions
│   │   └── security.py            # Auth & encryption utilities
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── user.py                # User model
│   │   ├── bank_account.py        # Bank account model
│   │   ├── transaction.py         # Transaction model
│   │   ├── budget.py              # Budget model
│   │   └── plaid_link_session.py  # Plaid session tracking
│   └── services/                   # Business logic services
│       ├── document_parser_service.py  # Parse financial docs
│       ├── investment_service.py      # Investment analysis
│       └── transaction_service.py     # Transaction processing
```

**Responsibilities:**
- API endpoint definitions
- Request validation (Pydantic)
- Business logic execution
- Database operations
- External API integration
- Authentication & authorization
- Error handling & logging

### 3. Data Layer (Database)

**PostgreSQL Schema:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bank accounts table
CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plaid_account_id VARCHAR(255) UNIQUE,
    plaid_item_id VARCHAR(255),
    account_name VARCHAR(255),
    account_type VARCHAR(50),
    account_subtype VARCHAR(50),
    current_balance DECIMAL(12, 2),
    available_balance DECIMAL(12, 2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    account_id INTEGER REFERENCES bank_accounts(id),
    plaid_transaction_id VARCHAR(255) UNIQUE,
    transaction_date DATE NOT NULL,
    posted_date DATE,
    amount DECIMAL(12, 2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    merchant_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    description TEXT,
    is_pending BOOLEAN DEFAULT FALSE,
    transaction_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budgets table
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly',
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plaid link sessions table
CREATE TABLE plaid_link_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    link_token TEXT NOT NULL,
    access_token TEXT,
    item_id VARCHAR(255),
    institution_id VARCHAR(255),
    institution_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'initiated',
    error_code VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Data Flow

### 1. User Authentication Flow

```
┌─────────┐      ┌─────────┐      ┌──────────┐
│  User   │      │ Mobile  │      │ Backend  │
└────┬────┘      └────┬────┘      └────┬─────┘
     │                │                 │
     │ Enter Creds    │                 │
     ├───────────────►│                 │
     │                │ POST /login     │
     │                ├────────────────►│
     │                │                 │ Verify Password
     │                │                 ├──────────┐
     │                │                 │          │
     │                │  JWT Token      │◄─────────┘
     │                │◄────────────────┤
     │                │ Store Token     │
     │                ├──────────┐      │
     │   Success      │          │      │
     │◄───────────────┤◄─────────┘      │
     │                │                 │
```

### 2. Plaid Bank Connection Flow

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐
│  User   │   │ Mobile  │   │ Backend │   │ Plaid  │
└────┬────┘   └────┬────┘   └────┬────┘   └───┬────┘
     │             │              │            │
     │ Connect Bank│              │            │
     ├────────────►│              │            │
     │             │ Request Token│            │
     │             ├─────────────►│            │
     │             │              │ Create Link│
     │             │              ├───────────►│
     │             │              │ Link Token │
     │             │  Link Token  │◄───────────┤
     │             │◄─────────────┤            │
     │  Open Plaid │              │            │
     │◄────────────┤              │            │
     │             │              │            │
     │ Select Bank │              │            │
     ├───────────────────────────►│            │
     │ Login       │              │            │
     ├───────────────────────────►│            │
     │             │              │            │
     │ Public Token│              │            │
     │◄───────────────────────────┤            │
     │             │              │            │
     │             │ Exchange     │            │
     │             ├─────────────►│            │
     │             │              │ Exchange   │
     │             │              ├───────────►│
     │             │              │Access Token│
     │             │              │◄───────────┤
     │             │  Access Token│            │
     │             │◄─────────────┤            │
     │             │ Store Token  │            │
     │             ├─────┐        │            │
     │   Connected │     │        │            │
     │◄────────────┤◄────┘        │            │
     │             │              │            │
```

### 3. Transaction Data Flow

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐
│  User   │   │ Mobile  │   │ Backend │   │  DB    │
└────┬────┘   └────┬────┘   └────┬────┘   └───┬────┘
     │             │              │            │
     │ View Trans  │              │            │
     ├────────────►│              │            │
     │             │ Check Local  │            │
     │             ├──────┐       │            │
     │             │      │       │            │
     │             │◄─────┘       │            │
     │             │ Fetch Latest │            │
     │             ├─────────────►│            │
     │             │              │ Query      │
     │             │              ├───────────►│
     │             │              │ Rows       │
     │             │              │◄───────────┤
     │             │  JSON Data   │            │
     │             │◄─────────────┤            │
     │             │ Cache Locally│            │
     │             ├──────┐       │            │
     │ Display     │      │       │            │
     │◄────────────┤◄─────┘       │            │
     │             │              │            │
```

### 4. Budget Calculation Flow

```
Mobile App (budgetData.ts)
    │
    ├─► Fetch Transactions (last 30 days)
    │       │
    │       └─► plaidLegacy.getTransactions()
    │               │
    │               └─► Backend: GET /api/plaid-legacy/transactions
    │                       │
    │                       └─► Plaid API: /transactions/get
    │
    ├─► Categorize Transactions
    │       │
    │       ├─► isIncome(category) → Income Detection
    │       └─► normalizeCategory(category) → Category Mapping
    │
    ├─► Calculate Totals
    │       │
    │       ├─► Sum Income
    │       ├─► Sum Expenses by Category
    │       └─► Calculate Net (Income - Expenses)
    │
    └─► Return DashboardData
            │
            └─► FinancialSummary.tsx → Display
```

---

## Component Interactions

### Mobile App Component Hierarchy

```
App.tsx
└── NavigationContainer
    └── BottomTabs
        ├── HomeScreen
        │   ├── FinancialSummary
        │   │   └── (Uses budgetData service)
        │   └── InvestmentAnalysis
        │       └── (Uses investmentApi service)
        │
        ├── TransactionsScreen
        │   └── (Uses plaidLegacy service)
        │
        ├── AddTransactionScreen
        │   └── (Manual entry form)
        │
        └── AccountScreen
            └── PlaidConnection
                └── (Uses plaidLegacy service)
```

### Backend Router Structure

```
FastAPI App (main.py)
├── Middleware
│   ├── CORS (allow mobile app)
│   └── Request logging
│
├── Routers
│   ├── /api/plaid-legacy/*
│   │   ├── POST /exchange-token
│   │   ├── GET /accounts
│   │   └── GET /transactions
│   │
│   ├── /api/v1/auth/*
│   │   ├── POST /register
│   │   ├── POST /login
│   │   └── GET /me
│   │
│   ├── /api/v1/banks/*
│   │   ├── GET /accounts
│   │   ├── POST /accounts
│   │   └── DELETE /accounts/{id}
│   │
│   └── /api/v1/insights/*
│       ├── GET /recommendations
│       ├── POST /analyze
│       └── GET /spending-analysis
│
└── Database Connection (PostgreSQL)
    └── Session Management (SQLAlchemy)
```

---

## API Endpoints

### Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Create new user account | No |
| POST | `/login` | Login and receive JWT token | No |
| GET | `/me` | Get current user profile | Yes |
| PUT | `/me` | Update user profile | Yes |

**Request/Response Examples:**

```typescript
// POST /api/v1/auth/login
Request: {
  email: "user@example.com",
  password: "secure_password"
}

Response: {
  access_token: "eyJhbGc...",
  token_type: "bearer",
  user: {
    id: 1,
    email: "user@example.com",
    full_name: "John Doe"
  }
}
```

### Plaid Integration Endpoints (`/api/plaid-legacy`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/create-link-token` | Generate Plaid Link token | Yes |
| POST | `/exchange-token` | Exchange public token for access token | Yes |
| GET | `/accounts` | Get bank accounts from Plaid | Yes |
| GET | `/transactions` | Get transactions from Plaid | Yes |
| GET | `/balance` | Get account balances | Yes |

**Request/Response Examples:**

```typescript
// POST /api/plaid-legacy/exchange-token
Request: {
  public_token: "public-sandbox-xxx",
  institution_id: "ins_109508",
  institution_name: "Chase"
}

Response: {
  access_token: "access-sandbox-xxx",
  item_id: "item-xxx"
}

// GET /api/plaid-legacy/transactions?start_date=2024-01-01&end_date=2024-01-31
Response: {
  transactions: [
    {
      transaction_id: "trans-xxx",
      account_id: "acc-xxx",
      amount: 12.50,
      date: "2024-01-15",
      name: "Starbucks",
      merchant_name: "Starbucks",
      category: ["Food and Drink", "Restaurants", "Coffee Shop"],
      pending: false
    }
  ]
}
```

### Bank Accounts Endpoints (`/api/v1/banks`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/accounts` | List user's bank accounts | Yes |
| GET | `/accounts/{id}` | Get specific account details | Yes |
| POST | `/accounts` | Create manual bank account | Yes |
| PUT | `/accounts/{id}` | Update account details | Yes |
| DELETE | `/accounts/{id}` | Remove bank account | Yes |
| POST | `/accounts/{id}/sync` | Sync transactions | Yes |

### Insights Endpoints (`/api/v1/insights`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/recommendations` | Get investment recommendations | Yes |
| POST | `/analyze` | Analyze spending patterns | Yes |
| GET | `/spending-analysis` | Get spending breakdown | Yes |
| POST | `/upload-portfolio` | Upload portfolio document | Yes |

---

## Authentication & Security

### JWT Token Flow

```
1. User logs in with credentials
2. Backend validates credentials
3. Backend generates JWT token with payload:
   {
     "sub": "user_id",
     "email": "user@example.com",
     "exp": "expiration_timestamp"
   }
4. Frontend stores token in AsyncStorage
5. All subsequent requests include token in header:
   Authorization: Bearer <token>
6. Backend validates token on each request
7. Token expires after 30 minutes (configurable)
```

### Security Measures

1. **Password Hashing**: bcrypt with salt rounds
2. **Token Storage**: AsyncStorage (development), secure storage (production)
3. **HTTPS**: Required for production API calls
4. **CORS**: Configured to allow only mobile app origin
5. **Environment Variables**: Sensitive data in `.env` files
6. **Database**: Connection pooling with SSL in production
7. **Plaid Tokens**: Encrypted access tokens stored in database

### Configuration (`.env`)

```env
# Application Mode
APP_MODE=live  # 'offline' for SQLite, 'live' for PostgreSQL

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Plaid API
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox  # sandbox, development, production

# PostgreSQL
POSTGRES_USER=budget_user
POSTGRES_PASSWORD=budget_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=budget_tracker
```

---

## External Integrations

### Plaid Banking API

**Purpose**: Securely connect to user bank accounts and retrieve financial data

**Integration Points:**
- `backend/app/api/plaid_legacy.py`: Backend proxy for Plaid API
- `mobile/src/services/plaidLegacy.ts`: Frontend Plaid client

**Data Retrieved:**
- Bank accounts (checking, savings, credit cards)
- Transaction history
- Account balances
- Institution information

**Flow:**
1. User initiates connection via PlaidConnection component
2. Backend creates Link Token
3. User authenticates with bank via Plaid Link
4. Frontend receives public token
5. Backend exchanges public token for access token
6. Access token stored securely for future API calls

**Security:**
- Plaid handles all bank credentials (never stored in app)
- Access tokens encrypted in database
- Sandbox mode for development
- Production mode requires Plaid approval

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────┐
│         Developer Machine (Windows)          │
├─────────────────────────────────────────────┤
│                                               │
│  ┌──────────────┐       ┌─────────────────┐ │
│  │ Mobile App   │       │ Backend API     │ │
│  │ (Expo Dev)   │       │ (uvicorn)       │ │
│  │ :8083        │◄─────►│ :8000           │ │
│  └──────────────┘       └────────┬────────┘ │
│                                   │          │
│                          ┌────────▼────────┐ │
│                          │ PostgreSQL      │ │
│                          │ :5432           │ │
│                          └─────────────────┘ │
└─────────────────────────────────────────────┘
```

**Commands:**
```powershell
# Backend
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Mobile
cd mobile
npm start
```

### Docker Compose Environment

```
┌─────────────────────────────────────────────┐
│              Docker Host                     │
├─────────────────────────────────────────────┤
│                                               │
│  ┌──────────────────┐    ┌────────────────┐ │
│  │ postgres         │    │ api            │ │
│  │ (PostgreSQL 16)  │◄───│ (FastAPI)      │ │
│  │ :5432            │    │ :8000          │ │
│  └──────────────────┘    └────────────────┘ │
│           │                                   │
│           ▼                                   │
│  ┌──────────────────┐                        │
│  │ postgres_data    │                        │
│  │ (Volume)         │                        │
│  └──────────────────┘                        │
└─────────────────────────────────────────────┘
         ▲
         │
┌────────┴─────────┐
│ Mobile App       │
│ (Host Machine)   │
│ localhost:8000   │
└──────────────────┘
```

**Commands:**
```powershell
cd infra
docker-compose up -d        # Start all services
docker-compose ps           # Check status
docker-compose logs -f api  # View logs
docker-compose down         # Stop services
```

### Production Architecture (Recommended)

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Provider                        │
│                  (AWS / Azure / GCP)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐     ┌────────────────┐     ┌────────┐ │
│  │ Load Balancer│────►│ API Instances  │────►│  RDS   │ │
│  │ (HTTPS)      │     │ (Container/VM) │     │  (PG)  │ │
│  └──────────────┘     └────────────────┘     └────────┘ │
│         ▲                      │                          │
│         │                      ▼                          │
│         │              ┌────────────────┐                 │
│         │              │ S3 / Blob      │                 │
│         │              │ (Documents)    │                 │
│         │              └────────────────┘                 │
│         │                                                  │
└─────────┼──────────────────────────────────────────────────┘
          │
┌─────────┴──────────┐
│ Mobile Apps        │
│ (iOS / Android)    │
│ https://api.domain │
└────────────────────┘
```

**Components:**
- **Load Balancer**: HTTPS termination, SSL certificates
- **API Instances**: Horizontal scaling, auto-scaling groups
- **Managed Database**: AWS RDS / Azure Database for PostgreSQL
- **Object Storage**: S3 / Azure Blob for document uploads
- **Mobile Apps**: Published to App Store / Play Store

---

## Configuration Modes

### Offline Mode (Development)
- **Database**: SQLite (`budget_tracker.db`)
- **Purpose**: Quick local development, no database setup
- **Configuration**: `APP_MODE=offline` in `.env`
- **Limitations**: Single user, no concurrent access

### Live Mode (Production)
- **Database**: PostgreSQL
- **Purpose**: Production deployment, multi-user support
- **Configuration**: `APP_MODE=live` in `.env`
- **Features**: Connection pooling, transactions, data integrity

**Switching Modes:**
```env
# Edit backend/.env
APP_MODE=offline  # Use SQLite
APP_MODE=live     # Use PostgreSQL
```

The application automatically adapts database configuration based on mode.

---

## Development Workflow

### Adding a New Feature

1. **Frontend (Mobile)**
   ```
   mobile/src/
   ├── screens/NewFeatureScreen.tsx    # Create screen
   ├── components/NewFeature.tsx       # Create component
   ├── services/newFeatureApi.ts       # Add API client
   └── types/index.ts                  # Add TypeScript types
   
   mobile/src/navigation/BottomTabs.tsx  # Add to navigation
   ```

2. **Backend (API)**
   ```
   backend/app/
   ├── api/new_feature.py              # Create router
   ├── models/new_feature.py           # Create model
   └── services/new_feature_service.py # Business logic
   
   backend/app/main.py                  # Register router
   ```

3. **Database Migration**
   ```python
   # backend/app/models/new_feature.py
   from sqlalchemy import Column, Integer, String
   from app.core.database import Base
   
   class NewFeature(Base):
       __tablename__ = "new_features"
       id = Column(Integer, primary_key=True)
       name = Column(String(255))
   ```

4. **Initialize Database**
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe init_db.py
   ```

### Testing Flow

1. **Start Backend**: `cd backend; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`
2. **Start Mobile**: `cd mobile; npm start`
3. **Test on Web**: Press `w` in Expo CLI
4. **Test on Device**: Scan QR code with Expo Go app

---

## Key Design Decisions

### 1. Why React Native (Expo)?
- **Cross-platform**: Single codebase for iOS and Android
- **Fast development**: Hot reload, extensive component library
- **Easy deployment**: Over-the-air updates with Expo
- **Native features**: Camera, storage, notifications

### 2. Why FastAPI?
- **Performance**: Async/await support, fast execution
- **Type safety**: Pydantic validation, automatic OpenAPI docs
- **Modern Python**: Python 3.13, type hints
- **Easy testing**: Built-in test client

### 3. Why PostgreSQL?
- **ACID compliance**: Data integrity for financial data
- **Scalability**: Handle millions of transactions
- **JSON support**: Store flexible data structures
- **Mature ecosystem**: Battle-tested, extensive tooling

### 4. Why Dual-Mode Database?
- **Development speed**: SQLite requires no setup
- **Production readiness**: PostgreSQL for real deployments
- **Flexibility**: Easy switching between modes

### 5. Why AsyncStorage (Current) vs Database (Future)?
- **Current**: Quick prototyping, demo functionality
- **Future**: Security, sync across devices, data persistence

---

## Future Enhancements

### Short Term
- [ ] Implement user authentication UI
- [ ] Enable database-backed bank accounts (banks.py router)
- [ ] Add transaction sync background job
- [ ] Implement budget tracking with alerts

### Medium Term
- [ ] Add push notifications
- [ ] Implement receipt scanning (OCR)
- [ ] Add data export features
- [ ] Create web dashboard

### Long Term
- [ ] Machine learning spending predictions
- [ ] Investment portfolio tracking
- [ ] Bill payment reminders
- [ ] Multi-currency support

---

## Troubleshooting Guide

### Common Issues

**Mobile App Can't Connect to Backend**
- Check backend is running: `http://localhost:8000/docs`
- Verify `API_BASE_URL` in mobile services
- Ensure CORS configured correctly in backend

**Database Connection Failed**
- Verify PostgreSQL is running: `docker-compose ps`
- Check credentials in `.env`
- Run `init_db.py` to create tables

**Plaid Integration Issues**
- Verify Plaid credentials in `.env`
- Check Plaid dashboard for API errors
- Use sandbox mode for development

**Build Errors**
- Clear Metro cache: `npm start -- --clear`
- Reinstall dependencies: `rm -rf node_modules; npm install`
- Check TypeScript errors: `npx tsc --noEmit`

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [Plaid API Documentation](https://plaid.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Last Updated**: December 2, 2025  
**Version**: 1.0  
**Maintainer**: SmartBudget Development Team
