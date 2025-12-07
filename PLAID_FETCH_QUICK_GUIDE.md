================================================================================
                    QUICK START GUIDE - PLAID FETCH FEATURE
================================================================================

WHAT WAS ADDED?
================================================================================

After a successful Plaid bank connection, users now see:

  1. TWO NEW BUTTONS
     📊 Fetch Accounts     (Green button, left side)
     💳 Fetch Transactions (Green button, right side)

  2. DATA DISPLAY SECTIONS (appear after clicking buttons)
     📊 Accounts - Shows all linked bank accounts with balances
     💳 Recent Transactions - Shows up to 10 recent transactions


HOW TO USE
================================================================================

Step 1: Connect Bank
  → Open "Connect Account" screen
  → Complete Plaid connection
  → See success message ✅

Step 2: Fetch Accounts (Optional)
  → Click "📊 Fetch Accounts" button
  → Accounts list displays below
  → Shows account name, type, mask, and balance

Step 3: Fetch Transactions (Optional)
  → Click "💳 Fetch Transactions" button
  → Recent transactions display below
  → Shows description, date, and amount


TESTING INSTRUCTIONS
================================================================================

Make sure you have BOTH running:

1. Backend (in terminal):
   cd backend
   uvicorn app.main:app --reload

2. Mobile App (in another terminal):
   cd mobile
   npm start

Then:

1. Open mobile app in browser (http://localhost:8083 or Expo app)
2. Navigate to "Connect Account" tab
3. Click "Connect with Plaid" button
4. Complete Plaid connection (use test bank credentials if available)
5. After success, you should see the new buttons:
   - "📊 Fetch Accounts"
   - "💳 Fetch Transactions"
6. Click buttons to fetch and display data


WHAT EACH BUTTON DOES
================================================================================

📊 FETCH ACCOUNTS BUTTON
├─ Calls: GET /api/plaid-legacy/accounts
├─ Shows: Loading spinner while fetching
├─ Displays:
│  ├─ Account Name (e.g., "Checking Account")
│  ├─ Account Mask (e.g., "•••• 1234")
│  ├─ Account Type (e.g., "Checking", "Savings")
│  └─ Balance (e.g., "$5,234.50")
└─ Colors: Cyan border, green balance text

💳 FETCH TRANSACTIONS BUTTON
├─ Calls: GET /api/plaid-legacy/transactions
├─ Shows: Loading spinner while fetching
├─ Displays: (up to 10 recent transactions)
│  ├─ Description (e.g., "Starbucks Coffee")
│  ├─ Date (e.g., "2025-12-03")
│  ├─ Amount (e.g., "-$6.50")
│  └─ Color: Red for outgoing, Green for incoming
└─ Indicator: "... and X more transactions" if more exist


VISUAL LAYOUT
================================================================================

After successful connection:

┌──────────────────────────────────────────────────┐
│              ✅ Bank Connected!                  │
│         Your Chase account is connected          │
├──────────────────────────────────────────────────┤
│  Status: Active        Auto Sync: Enabled        │
│  Sync Frequency: Daily    Last Sync: Just now    │
├──────────────────────────────────────────────────┤
│   [📊 Fetch Accounts]    [💳 Fetch Transactions]│  ← NEW
├──────────────────────────────────────────────────┤
│  📊 Accounts (2)                                 │  ← NEW (if clicked)
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│  ┃ Checking Account                             ┃
│  ┃ •••• 1234  Checking                          ┃
│  ┃ $5,234.50                                    ┃
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│  ┃ Savings Account                              ┃
│  ┃ •••• 5678  Savings                           ┃
│  ┃ $10,500.00                                   ┃
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
├──────────────────────────────────────────────────┤
│  💳 Recent Transactions (25)                     │  ← NEW (if clicked)
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│  ┃ Starbucks Coffee               -$6.50       ┃
│  ┃ 2025-12-03                                   ┃
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│  ┃ Salary Deposit                 +$3,500.00   ┃
│  ┃ 2025-12-01                                   ┃
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│  ┃ ATM Withdrawal                 -$100.00     ┃
│  ┃ 2025-12-02                                   ┃
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
│  ... and 22 more transactions                   │
├──────────────────────────────────────────────────┤
│              [Disconnect Bank]                  │
└──────────────────────────────────────────────────┘

Color Key:
  🟦 Cyan border = Account cards
  🟧 Amber border = Transaction cards
  🟢 Green = Positive amounts / Buttons
  🔴 Red = Negative amounts


TROUBLESHOOTING
================================================================================

Issue: Buttons don't appear
  → Check: Did you complete Plaid connection successfully?
  → Fix: Try connecting again

Issue: Buttons appear but nothing happens when clicked
  → Check: Is backend running? (http://localhost:8000/docs)
  → Fix: Start backend: uvicorn app.main:app --reload

Issue: Error alert appears
  → Check: Backend console for errors
  → Check: Network tab in browser dev tools
  → Fix: Ensure /api/plaid-legacy/* endpoints are implemented

Issue: Data displays but looks incomplete
  → Check: Response format in backend
  → Fix: Review REQUIREMENTS_EXPLANATION.txt for expected format


TECHNICAL DETAILS
================================================================================

State Management:
  - accountsData: Account[]
  - transactionsData: Transaction[]
  - showAccounts: boolean (toggle display)
  - showTransactions: boolean (toggle display)
  - loadingAccounts: boolean (show spinner)
  - loadingTransactions: boolean (show spinner)

API Calls:
  - GET /api/plaid-legacy/accounts
    Response: { accounts: [...] }
  - GET /api/plaid-legacy/transactions
    Response: { transactions: [...] }

Authentication:
  - Uses makeAuthenticatedRequest helper
  - Automatically includes auth token in headers
  - Requires user to be authenticated

Error Handling:
  - try/catch blocks around API calls
  - Alert dialogs for user feedback
  - Console logging for debugging


KEY CODE LOCATIONS
================================================================================

File: mobile/src/screens/ConnectAccountScreen.tsx

Fetch Functions (lines ~129-174):
  - fetchAccounts(): Calls accounts endpoint
  - fetchTransactions(): Calls transactions endpoint

Render Section (lines ~291-363):
  - Fetch buttons
  - Accounts display
  - Transactions display

Styles (lines ~501-598):
  - Button styling
  - Card styling
  - Color scheme


FEATURES
================================================================================

✅ Real-time account data
✅ Recent transaction history
✅ Loading indicators
✅ Error handling
✅ Responsive layout
✅ Color-coded data
✅ Account masking (privacy)
✅ Transaction limit (shows "... and X more")
✅ Easy to extend with more endpoints


KNOWN LIMITATIONS
================================================================================

Current Implementation:
  - Shows first 10 transactions only (backend can limit)
  - No sorting/filtering options
  - No data caching (fetches fresh each time)
  - No refresh button (can click multiple times)

Future Enhancements:
  - Add pagination for more transactions
  - Add filters (date range, category, etc.)
  - Cache data locally
  - Add auto-refresh timer
  - Export to CSV


GETTING HELP
================================================================================

For Issues:
  1. Check browser console (F12 → Console tab)
  2. Check backend logs (terminal where uvicorn runs)
  3. Check network tab (F12 → Network tab)
  4. Review endpoint responses in /docs (http://localhost:8000/docs)

For Questions:
  1. Read: mobile/PLAID_ACCOUNT_FETCH_FEATURE.md (detailed docs)
  2. Check: backend/app/api/plaid_legacy.py (endpoint implementation)
  3. Review: backend/app/services/plaid_service_legacy.py (business logic)


QUICK REFERENCE
================================================================================

What's New?
  ✨ Fetch Accounts button
  ✨ Fetch Transactions button
  ✨ Accounts display section
  ✨ Transactions display section
  ✨ 40+ new style properties
  ✨ 8 new state variables
  ✨ 2 new async functions

Where?
  📱 ConnectAccountScreen - After successful Plaid connection
  
When?
  ⏰ Immediately after bank is connected
  
How?
  👆 Click the green fetch buttons
  
Result?
  ✅ Account and transaction data displayed
  
Next Step?
  → Test it out!


================================================================================
That's it! You're ready to test the new feature. 🚀
================================================================================
