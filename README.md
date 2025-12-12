# SmartBudget - Personal Finance Tracker

A modern personal finance tracking application built with React Native (Expo) and FastAPI, featuring automated bank account integration via Plaid, AI-powered spending analysis, and investment recommendations.

## 🚀 Features

- **Bank Account Integration**: Connect your bank accounts securely via Plaid
- **Automated Transaction Sync**: Automatically fetch and categorize transactions
- **Manual Entry**: Add custom income and expense entries
- **Financial Insights**: Dynamic charts showing spending trends and financial activity
- **Category Analysis**: Track spending across different categories
- **Investment Analysis**: Get personalized investment recommendations
- **Real-time Updates**: Live synchronization with your financial data

## 🏗️ Architecture

### Frontend (Mobile App)
- **Framework**: React Native with Expo
- **Language**: TypeScript
- **UI**: Custom components with animations
- **Navigation**: Bottom tab navigation
- **State Management**: React Context API
- **Database**: Supabase (PostgreSQL)

### Backend (API)
- **Framework**: FastAPI (Python)
- **Integration**: Plaid API for bank connections
- **Database**: Supabase
- **Features**: Transaction sync, AI analysis, investment recommendations

## 📋 Prerequisites

- Docker and Docker Compose
- Expo Go app on your mobile device (for testing)
- Internet connection for Plaid API access

## 🛠️ Quick Start with Docker

### 1. Build and Start Services

From the project root directory:

```bash
docker-compose build
docker-compose up -d
```

This will start:
- **Backend API**: Running on `http://localhost:8001`
- **Mobile App**: Expo dev server on `http://localhost:19000`

### 2. Access Points

- **Backend API Documentation**: http://localhost:8001/docs
- **Backend Health Check**: http://localhost:8001/health
- **Expo Dev Server**: http://localhost:19000

### 3. Connect with Expo Go

1. Install Expo Go on your mobile device
2. Open Expo Go app
3. Scan the QR code from the terminal or from http://localhost:19000
4. The app will load on your device

### 4. Test Credentials

The app comes with pre-configured Plaid Sandbox test credentials:

**Supabase Login:**
- Username: `user_ewa_user@good`
- Password: `abc123`

**Plaid Sandbox Bank:**
This account is already connected to Plaid Sandbox Bank with test transaction data.

## 📱 Mobile App Structure

```
mobile/
├── App.tsx                 # Main app entry point
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── AnimatedChart.tsx
│   │   ├── FinancialActivityRings.tsx
│   │   ├── FinancialSummary.tsx
│   │   ├── PlaidConnection.tsx
│   │   └── ...
│   ├── screens/            # Main app screens
│   │   ├── HomeScreen.tsx
│   │   ├── TransactionsScreen.tsx
│   │   ├── ConnectAccountScreen.tsx
│   │   └── AccountScreen.tsx
│   ├── navigation/         # Navigation configuration
│   │   └── BottomTabs.tsx
│   ├── services/           # API and data services
│   │   ├── plaidTransactionService.ts
│   │   ├── supabaseClient.ts
│   │   └── ...
│   ├── context/            # React Context providers
│   │   └── AuthContext.tsx
│   └── types/              # TypeScript type definitions
└── package.json
```

## 🔧 Backend API Structure

```
backend/
├── main.py                 # FastAPI main application
├── requirements.txt        # Python dependencies
├── services/               # Service modules
│   ├── plaidService.ts
│   ├── config.ts
│   └── ...
└── types/                  # Type definitions
```

## 🔌 API Endpoints

### Plaid Integration

- `POST /api/plaid/create-link-token` - Create a Plaid Link token
- `POST /api/plaid/exchange-token` - Exchange public token for access token
- `POST /api/plaid/accounts` - Get connected bank accounts
- `POST /api/plaid/transactions` - Get transactions for a date range
- `POST /api/plaid/sync_transactions` - Sync latest transactions (last 30 days)

### Plaid Sandbox Testing

- `POST /api/plaid/sandbox/public_token` - Create sandbox test account
- `POST /api/plaid/sandbox/custom_user` - Create custom test user with specific data

### AI Analysis

- `POST /api/ai/analyze_spending` - Get AI-powered spending analysis
- `POST /api/ai/investment_advice` - Get personalized investment recommendations

## 🎯 Usage Guide

### 1. Login
- Open the app and log in with the test credentials
- You'll be redirected to the home screen

### 2. Home Screen
- View your financial activity rings (Budget, Savings, Investment)
- Check monthly spending trends in the animated chart
- Review financial summary with income, expenses, and net balance
- Explore category breakdowns

### 3. Transactions Screen
- View all your transactions
- Add manual entries:
  - Enter amount
  - Add description
  - Select date (improved date picker!)
  - Choose category (Food, Transport, Bills, Shopping, Fun, Other)
- Edit or delete existing transactions
- View spending breakdown by category

### 4. Connect Account Screen
- Connect additional bank accounts via Plaid
- Manage connected accounts
- Configure auto-sync settings

### 5. Account Screen
- View profile information
- Manage settings
- Log out

## 🔐 Security Notes

- All bank connections are secured via Plaid's encryption
- Test environment uses Plaid Sandbox (no real bank data)
- For production use, ensure proper environment variables and security measures

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### View logs
```bash
# Backend logs
docker-compose logs backend

# Mobile app logs
docker-compose logs mobile

# All logs
docker-compose logs -f
```

### Reset database
Supabase database can be reset via the Supabase dashboard or by reinitializing the schema.

## 🛑 Stopping Services

```bash
docker-compose down
```

To also remove volumes:
```bash
docker-compose down -v
```

## 🚀 Development

### Run Backend Locally (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Run Mobile App Locally (without Docker)

```bash
npm install
npm start
```

## 📝 Environment Variables

The app uses the following environment variables (configured in Docker):

```
EXPO_PUBLIC_API_URL=http://10.0.0.214:8001
PLAID_CLIENT_ID=68f9e88c17270900222dae83
PLAID_SECRET=ce8fb384dc57b556987e6874f719d9
PLAID_ENV=sandbox
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Plaid for banking integration
- Supabase for backend infrastructure
- Expo for mobile development framework
- FastAPI for the backend API

---

**Note**: This is a test environment using Plaid Sandbox. For production deployment, proper security measures, environment configuration, and compliance with financial regulations must be implemented.
