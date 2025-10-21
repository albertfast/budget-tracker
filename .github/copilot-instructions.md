# Copilot Instructions for SmartBudget

## Project Overview
SmartBudget is a personal finance tracker with a **React Native (Expo)** mobile frontend and a **FastAPI (Python)** backend. The project is organized into:
- `mobile/`: Expo React Native app (TypeScript)
- `backend/`: FastAPI backend (Python)
- `infra/`: Docker Compose, database, CI/CD
- `docs/`: Planning and documentation

## Architecture & Data Flow
- **Mobile app** communicates with the backend via REST API endpoints (see `backend/app/api/`).
- **Backend** exposes endpoints for transactions, accounts, budgets, and manual entries. Core logic is in `backend/app/core/`.
- **Database** is PostgreSQL, managed via Docker Compose (`infra/docker-compose.yml`).
- **Authentication** and bank integration are planned but not yet implemented.

## Developer Workflows
- **Mobile:**
  - Install dependencies: `npm install` in `mobile/`
  - Start app: `npm start` or `expo start`
  - Main entry: `mobile/App.tsx`
  - Navigation: `mobile/src/navigation/BottomTabs.tsx`
  - Screens: `mobile/src/screens/`
- **Backend:**
  - Create venv: `python -m venv .venv` in `backend/`
  - Activate: `source .venv/bin/activate`
  - Install: `pip install -r requirements.txt`
  - Run: `uvicorn app.main:app --reload`
  - Main entry: `backend/app/main.py`
- **Infra:**
  - Start all services: `docker-compose up` in `infra/`

## Conventions & Patterns
- **Branch naming:** `feature/<name>`, `fix/<name>`
- **Pull requests:** Require review before merge
- **API endpoints:** Defined in `backend/app/api/`, follow RESTful conventions
- **Mobile navigation:** Bottom tab navigation, each screen in its own file
- **TypeScript:** Used for mobile app, types in `mobile/src/types/`
- **Python:** Backend code organized by domain (core, api)

## Integration Points
- **Mobile <-> Backend:** All data flows through REST API endpoints
- **Database:** Backend uses PostgreSQL, configured in Docker Compose
- **CI/CD:** GitHub Actions planned for automated testing/deployment

## Key Files & Directories
- `mobile/App.tsx`: Mobile app entry
- `mobile/src/screens/`: Main screens (Home, Transactions, Add, Account)
- `backend/app/main.py`: FastAPI entrypoint
- `backend/app/api/`: API route definitions
- `backend/app/core/`: Business logic
- `infra/docker-compose.yml`: Service orchestration

## Examples
- To add a new screen: create a file in `mobile/src/screens/`, add to navigation in `BottomTabs.tsx`
- To add a new API route: create a module in `backend/app/api/`, register in `main.py`

---
For questions about unclear conventions or missing documentation, ask for clarification in the README or project board.
