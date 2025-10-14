# Budget Tracker - Git Workflow Script
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "sync", "push", "pull", "commit", "backup", "setup")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Message = "Update: incremental changes and improvements"
)

function Write-Header($Text) {
    Write-Host "`n🚀 $Text" -ForegroundColor Cyan
    Write-Host ("=" * ($Text.Length + 4)) -ForegroundColor DarkCyan
}

function Write-Success($Text) {
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Info($Text) {
    Write-Host "ℹ️  $Text" -ForegroundColor Yellow
}

function Write-Error($Text) {
    Write-Host "❌ $Text" -ForegroundColor Red
}

switch ($Action) {
    "status" {
        Write-Header "Git Status Check"
        Write-Info "Current branch and status:"
        git branch --show-current
        git status --short
        Write-Info "Recent commits:"
        git log --oneline -5
    }
    
    "sync" {
        Write-Header "Syncing with Upstream"
        Write-Info "Fetching latest changes from upstream..."
        git fetch upstream
        Write-Info "Fetching from origin..."
        git fetch origin
        Write-Success "Sync completed!"
    }
    
    "push" {
        Write-Header "Quick Push to GitHub"
        Write-Info "Staging all changes..."
        git add .
        
        Write-Info "Committing with message: $Message"
        git commit -m $Message
        
        Write-Info "Pushing to origin..."
        git push
        Write-Success "Changes pushed successfully!"
    }
    
    "pull" {
        Write-Header "Pulling Latest Changes"
        Write-Info "Pulling from current branch..."
        git pull
        Write-Success "Pull completed!"
    }
    
    "commit" {
        Write-Header "Committing Changes"
        Write-Info "Staging all changes..."
        git add .
        Write-Info "Committing with message: $Message"
        git commit -m $Message
        Write-Success "Changes committed locally!"
    }
    
    "backup" {
        Write-Header "Creating Backup"
        $timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm"
        $backupBranch = "backup-$timestamp"
        
        Write-Info "Creating backup branch: $backupBranch"
        git checkout -b $backupBranch
        git add .
        git commit -m "Backup: $timestamp"
        git push -u origin $backupBranch
        git checkout -
        Write-Success "Backup created and pushed!"
    }
    
    "setup" {
        Write-Header "Git Setup Information"
        Write-Info "Repository remotes:"
        git remote -v
        Write-Info "Current branch:"
        git branch --show-current
        Write-Info "All branches:"
        git branch -a
        Write-Info "Recent activity:"
        git log --oneline -10
    }
}

Write-Host "`n💡 Available commands:" -ForegroundColor Magenta
Write-Host "  .\git-workflow.ps1 status     # Check current status"
Write-Host "  .\git-workflow.ps1 sync       # Sync with upstream"  
Write-Host "  .\git-workflow.ps1 push       # Quick commit and push"
Write-Host "  .\git-workflow.ps1 pull       # Pull latest changes"
Write-Host "  .\git-workflow.ps1 commit     # Commit without pushing"
Write-Host "  .\git-workflow.ps1 backup     # Create backup branch"
Write-Host "  .\git-workflow.ps1 setup      # Show setup info"