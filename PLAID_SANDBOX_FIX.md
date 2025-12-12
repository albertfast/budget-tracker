# Plaid Sandbox Authentication Fix

## Problem
When using Supabase authentication with email addresses like `user_ewa_user@good`, Plaid Sandbox would reject the credentials because it expects usernames without the domain part (e.g., `user_ewa_user`).

## Solution
Created an automated flow that:
1. Strips the email domain before sending to Plaid (`user_ewa_user@good` → `user_ewa_user`)
2. Programmatically creates a sandbox public token
3. Exchanges it for an access token
4. Fetches bank accounts automatically

## What Changed

### Backend (`backend/main.py`)
- Added helper function `_plaid_username_from_email()` to strip email domains
- Added new endpoint: `POST /api/plaid/sandbox/public_token`
  - Accepts: `{ "email": "user@domain.com", "password": "pass", "institution_id": "ins_109508" }`
  - Returns: `{ "public_token": "public-sandbox-...", "request_id": "..." }`

### Mobile App (`src/components/PlaidConnection.tsx`)
- Fixed network URL detection (use LAN IP `10.0.0.214:8001` instead of Docker internal `backend:8001`)
- Integrated with Supabase Auth to get user email
- Automated the sandbox flow (no manual Link UI needed)

## How to Test

### 1. Login with Supabase Credentials
```
Email: user_ewa_user@good
Password: abc123
```

### 2. Navigate to Connect Account Screen
The app will automatically:
- Extract `user_ewa_user` from your email
- Call backend to create sandbox token
- Exchange for access token
- Fetch accounts

### 3. Verify Backend Endpoint (Optional)
```bash
curl -X POST http://localhost:8001/api/plaid/sandbox/public_token \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user_ewa_user@good",
    "password": "abc123",
    "institution_id": "ins_109508"
  }'
```

Expected response:
```json
{
  "public_token": "public-sandbox-...",
  "request_id": "..."
}
```

## Valid Plaid Sandbox Credentials

Use these test credentials in Supabase for testing:

| Email in Supabase       | Plaid Username  | Password   | Result |
|-------------------------|-----------------|------------|--------|
| user_good@good          | user_good       | pass_good  | ✅ Success |
| user_ewa_user@good      | user_ewa_user   | abc123     | ✅ Success |
| user_custom@test        | user_custom     | pass_good  | ✅ Custom data |

The app now automatically strips `@good` or any domain when talking to Plaid.

## Network Configuration

### For Expo Go on Physical Device
- Backend URL: `http://10.0.0.214:8001` (your computer's LAN IP)
- Make sure both phone and computer are on the same WiFi network

### For iOS Simulator / Android Emulator
- Backend URL: `http://localhost:8001`

The app now automatically detects and uses the correct URL.

## Troubleshooting

### "Network request failed"
- Verify backend is running: `docker-compose ps`
- Check your LAN IP hasn't changed: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- Update `API_BASE_URL` in PlaidConnection.tsx if IP changed

### "Plaid error: invalid credentials"
- Ensure your Supabase email follows pattern: `<plaid_username>@<domain>`
- Password should match the Plaid sandbox password (e.g., `abc123`, `pass_good`)
- Backend automatically strips everything after `@`

### Backend not responding
```bash
# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs backend

# Verify endpoint
curl http://localhost:8001/health
```
