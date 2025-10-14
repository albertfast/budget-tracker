param(
    [string]$Action = "help",
    [string]$Message = "Update: incremental changes"
)

switch ($Action) {
    "status" {
        Write-Host "Git Status:" -ForegroundColor Green
        git status --short
        git branch --show-current
    }
    "push" {
        Write-Host "Quick Push:" -ForegroundColor Green
        git add .
        git commit -m $Message
        git push
    }
    "pull" {
        Write-Host "Pulling changes:" -ForegroundColor Green
        git pull
    }
    "sync" {
        Write-Host "Syncing with upstream:" -ForegroundColor Green
        git fetch upstream
        git fetch origin
    }
    default {
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  .\simple-git.ps1 status"
        Write-Host "  .\simple-git.ps1 push"
        Write-Host "  .\simple-git.ps1 pull"
        Write-Host "  .\simple-git.ps1 sync"
    }
}