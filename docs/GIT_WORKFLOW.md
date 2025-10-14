# Efficient Git Workflow for Budget Tracker

## Quick Setup Summary

Your repository is now configured with:
- **Origin**: `https://github.com/Head2MyToes/budget-tracker.git` (your fork)
- **Upstream**: `https://github.com/albertfast/budget-tracker.git` (original repo)
- **Current Branch**: `feature/comprehensive-financial-enhancements`

## Quick Commands

### PowerShell Script (Recommended)
```powershell
# Check status
.\git-workflow.ps1 status

# Quick commit and push
.\git-workflow.ps1 push -Message "feat: add new feature"

# Sync with upstream
.\git-workflow.ps1 sync

# Pull latest changes
.\git-workflow.ps1 pull

# Create backup
.\git-workflow.ps1 backup
```

### Batch File (Simple)
```cmd
# Quick push
quickgit push "your commit message"

# Check status
quickgit status

# Sync repositories
quickgit sync
```

### Direct Git Commands
```bash
# Quick push workflow
git add .
git commit -m "your message"
git push

# Pull latest changes
git pull

# Sync with upstream
git fetch upstream
git fetch origin
```

## Workflow Strategies

### 1. Daily Development Workflow
```powershell
# Start of day - sync with latest changes
.\git-workflow.ps1 sync
.\git-workflow.ps1 pull

# During development - frequent commits
.\git-workflow.ps1 push -Message "wip: working on feature X"

# End of day - comprehensive commit
.\git-workflow.ps1 push -Message "feat: complete feature X implementation"
```

### 2. Feature Development
```powershell
# Create feature branch
git checkout -b feature/new-feature-name

# Develop and commit frequently
.\git-workflow.ps1 push -Message "feat: add component A"
.\git-workflow.ps1 push -Message "feat: integrate component A with B"

# Push feature branch
git push -u origin feature/new-feature-name
```

### 3. Emergency Backup
```powershell
# Quick backup before major changes
.\git-workflow.ps1 backup
```

## Branch Management

### Current Setup
- **Main Development**: `feature/comprehensive-financial-enhancements`
- **Upstream Tracking**: Syncs with `albertfast/budget-tracker`
- **Your Fork**: `Head2MyToes/budget-tracker`

### Recommended Branch Strategy
1. **feature/*** - New features
2. **fix/*** - Bug fixes  
3. **docs/*** - Documentation updates
4. **backup-*** - Automatic backups

### Creating New Feature Branches
```bash
# From main development branch
git checkout feature/comprehensive-financial-enhancements
git pull
git checkout -b feature/your-new-feature
git push -u origin feature/your-new-feature
```

## Commit Message Conventions

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `style:` - Code formatting
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### Examples
```
feat: add Plaid integration for bank connections
fix: resolve transaction validation issue
docs: update API documentation
style: improve component styling consistency
refactor: reorganize service layer architecture
```

## Advanced Git Operations

### Syncing with Upstream Changes
```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your feature branch
git checkout feature/comprehensive-financial-enhancements
git merge upstream/main

# Push updated branch
git push origin feature/comprehensive-financial-enhancements
```

### Squashing Commits for Clean History
```bash
# Interactive rebase for last 3 commits
git rebase -i HEAD~3

# Push with force (only on feature branches)
git push --force-with-lease
```

### Creating Pull Requests
After pushing your feature branch, create a pull request:
1. Go to: https://github.com/Head2MyToes/budget-tracker
2. Click "Compare & pull request"
3. Target: `albertfast/budget-tracker:main`
4. Source: `Head2MyToes/budget-tracker:feature/your-branch`

## Troubleshooting

### If Push is Rejected
```bash
# Pull latest changes first
git pull --rebase
git push
```

### If You Need to Reset
```bash
# Soft reset (keeps changes)
git reset --soft HEAD~1

# Hard reset (discards changes)
git reset --hard HEAD~1
```

### If You Want to Undo Last Commit
```bash
# Keep changes in working directory
git reset --soft HEAD~1

# Remove changes completely
git reset --hard HEAD~1
```

## Automation Tips

### Set Up Git Aliases
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.ps push
git config --global alias.pl pull
```

### PowerShell Profile Setup
Add to your PowerShell profile:
```powershell
function gst { git status }
function gco { git checkout $args }
function gcm { git commit -m $args }
function gps { git push }
function gpl { git pull }
function quickpush { 
    param([string]$msg = "Update: incremental changes")
    git add .; git commit -m $msg; git push 
}
```

## Security Notes

- Never commit sensitive data (API keys, passwords)
- Use `.gitignore` for environment files
- Review changes before committing
- Use signed commits for verification

Your repository is now set up for efficient development! 🚀