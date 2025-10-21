# 🧠 Team GitHub Pull Request Guide

This guide explains how to properly clone, set up, and contribute to a GitHub repository using a fork and pull request (PR) model. It is intended for teammates like `vs-turner`, `head2mytoes`, `npad10`, and others.

## 🔰 Scenario: You downloaded the ZIP or cloned the original repo directly
If you did **not fork first**, or if you **downloaded the project as a ZIP**, follow these steps.

---

## 🧱 1. Initialize Git (if needed)
```bash
cd budget-tracker
# If no Git setup yet
git init
```

---

## 🙋 2. Configure your identity (just once per system)
```bash
git config user.name "your-github-username"
git config user.email "your-email@example.com"
```

---

## 🍴 3. Fork the Original Repo from GitHub UI
Go to:
```
https://github.com/albertfast/budget-tracker
```
Click the **Fork** button (top right). It will create:
```
https://github.com/your-username/budget-tracker
```

---

## 🔗 4. Link Your Fork as "origin"
```bash
git remote add origin https://github.com/your-username/budget-tracker.git
```

---

## 🧬 5. Link the Original Repo as "upstream"
```bash
git remote add upstream https://github.com/albertfast/budget-tracker.git
```

---

## 🔄 6. Sync Your Local Code With the Original Repo
```bash
git checkout -b main       # Or switch to main if already exists

# Pull changes from original project
git fetch upstream
git pull upstream main

# Push updates to your fork
git push origin main
```

---

## 🌿 7. Create a New Branch for Your Work
```bash
git checkout -b your_feature_branch
```
Use descriptive names like:
- `fix/login-validation`
- `feature/add-currency-selector`

---

## 💻 8. Make Your Changes
Edit files, add features, or fix bugs.

Check your status:
```bash
git status
```

Stage and commit changes:
```bash
git add .
git commit -m "Explain what you changed"
```

---

## ☁️ 9. Push Your Branch to Your Fork
```bash
git push origin your_feature_branch
```

---

## 🔀 10. Open a Pull Request on GitHub
Go to:
```
https://github.com/your-username/budget-tracker
```
You will see a "Compare & pull request" button. Open a PR from:
```
your-username:your_feature_branch
   → albertfast:main
```
Add a clear title and description of your changes.

---

## 🧭 11. Keeping Your Fork Up-To-Date (After Merge or Team Updates)
```bash
git checkout main

git fetch upstream
git pull upstream main

git push origin main
```

> ⚠️ If your PR is merged but you start a new feature: **always pull `upstream/main` first.**

---

## 🔍 Extras

### Show All Branches
```bash
git branch -a
```

### Show All Remotes
```bash
git remote -v
```

---

## ✅ Summary Checklist
```
[ ] Fork the repo on GitHub
[ ] Clone or unzip into local machine
[ ] Add your fork as 'origin'
[ ] Add original repo as 'upstream'
[ ] Pull changes from upstream
[ ] Push to origin
[ ] Create a new feature branch
[ ] Commit your changes
[ ] Push the branch
[ ] Open a Pull Request
[ ] Keep your fork updated
```

---

## 💬 Questions?
Ask your teammates or instructors if you’re unsure before pushing or opening a PR.

---

Happy coding! 💻✨

