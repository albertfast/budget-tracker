# budget-tracker
# SmartBudget
# This project for City College of San Francisco - CS 177-Software Engineering 
SmartBudget is a simple personal finance tracker built with **Expo (React Native)** for mobile and **FastAPI (Python)** for the backend.  
It helps users connect their bank, fetch transactions, categorize spending, add manual expenses, and receive alerts when budgets or limits are exceeded.

---

## 🍴 Fork This Repository

**Want to contribute?** Click the button below to fork this repository to your own GitHub account:

[![Fork budget-tracker](https://img.shields.io/badge/Fork-this%20repo-blue?style=for-the-badge&logo=github)](https://github.com/albertfast/budget-tracker/fork)

Or visit: **[https://github.com/albertfast/budget-tracker/fork](https://github.com/albertfast/budget-tracker/fork)**

📚 For detailed fork and contribution workflow, see [team_pr_guide.md](team_pr_guide.md)

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

### For Contributors (Recommended)

1. **Fork this repository** (click the Fork button above or visit [/fork](https://github.com/albertfast/budget-tracker/fork))
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/budget-tracker.git
   cd budget-tracker
   ```
3. **Set up remotes** (see [team_pr_guide.md](team_pr_guide.md) for details)
   ```bash
   git remote add upstream https://github.com/albertfast/budget-tracker.git
   ```

### For Quick Testing Only

1. **Clone the repo**
   ```bash
   git clone https://github.com/albertfast/budget-tracker.git
   cd budget-tracker
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
