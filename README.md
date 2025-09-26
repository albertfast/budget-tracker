# budget-tracker
# SmartBudget
# This project for City College of San Francisco - CS 177-Software Engineering 
SmartBudget is a simple personal finance tracker built with **Expo (React Native)** for mobile and **FastAPI (Python)** for the backend.  
It helps users connect their bank, fetch transactions, categorize spending, add manual expenses, and receive alerts when budgets or limits are exceeded.

---

## 🚀 Features (Planned)

- **Secure bank connection** (via third-party provider or CSV upload)
- **Automatic transaction sync & categorization**
- **Manual income/expense entry**
- **Budgets & custom alerts** (e.g. "Food > $500 this month")
- **Monthly insights & reports**
- **Cross-platform mobile app** (iOS & Android via Expo)

---

## 📂 Project Structure

```
smartbudget/
├─ mobile/           # Expo React Native app
├─ backend/          # FastAPI backend service
├─ infra/            # Docker compose, db, etc.
└─ docs/             # diagrams, planning docs
```

---

## 🛠️ Tech Stack

- **Mobile:** React Native + Expo
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Infra:** Docker Compose, GitHub Actions (CI/CD)

---

## 💻 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/albertfast/budget-tracker.git
   cd smartbudget
   ```

2. **Setup mobile app**
   ```bash
   cd mobile
   npm install expo
   npx expo start
   ```

3. **Setup backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

---

## 👤 Maintainers

- [albertfast](https://github.com/albertfast)
- [vs-turner](https://github.com/vs-turner)
- [head2mytoes](https://github.com/head2mytoes)
- [npad10](https://github.com/npad10)

## 👥 Team & Collaboration

- Work tracked on GitHub Projects (Kanban board).
- Branch naming: budget_tracker_start.
- Pull requests reviewed by at least one teammate.
- Issues used for tasks and backlog items.

---

## 📄 License

MIT License (to be confirmed by the team).
