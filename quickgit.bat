@echo off
REM Quick Git Commands for Budget Tracker
REM Usage: quickgit.bat [command] [message]

if "%1"=="push" (
    powershell -ExecutionPolicy Bypass -File "git-workflow.ps1" push -Message "%~2"
) else if "%1"=="status" (
    powershell -ExecutionPolicy Bypass -File "git-workflow.ps1" status
) else if "%1"=="sync" (
    powershell -ExecutionPolicy Bypass -File "git-workflow.ps1" sync
) else if "%1"=="pull" (
    powershell -ExecutionPolicy Bypass -File "git-workflow.ps1" pull
) else if "%1"=="backup" (
    powershell -ExecutionPolicy Bypass -File "git-workflow.ps1" backup
) else (
    echo.
    echo 🚀 Quick Git Commands for Budget Tracker
    echo ==========================================
    echo.
    echo Usage:
    echo   quickgit status                    # Check status
    echo   quickgit sync                      # Sync with upstream
    echo   quickgit push "commit message"     # Quick commit and push
    echo   quickgit pull                      # Pull latest changes
    echo   quickgit backup                    # Create backup
    echo.
    echo Examples:
    echo   quickgit push "feat: add new component"
    echo   quickgit push "fix: resolve UI issue"
    echo   quickgit push "docs: update README"
    echo.
)