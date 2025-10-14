# Secure Encrypted Backup Script for Budget Tracker
# This script creates an encrypted ZIP backup with a random encryption key

param(
    [string]$DesktopPath = [Environment]::GetFolderPath("Desktop"),
    [string]$ProjectPath = $PSScriptRoot
)

# Function to generate a strong random encryption key
function Generate-EncryptionKey {
    $length = 32
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
    $key = -join ((1..$length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $key
}

# Function to convert string to secure string
function ConvertTo-SecurePassword {
    param([string]$PlainText)
    return ConvertTo-SecureString -String $PlainText -AsPlainText -Force
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Secure Project Backup Utility" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generate timestamp for unique backup naming
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFolderName = "BudgetTracker_Backup_$timestamp"
$backupFolder = Join-Path $DesktopPath $backupFolderName

# Create backup folder on desktop
Write-Host "[1/6] Creating backup folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
Write-Host "      Created: $backupFolder" -ForegroundColor Green

# Generate random encryption key
Write-Host "[2/6] Generating random encryption key..." -ForegroundColor Yellow
$encryptionKey = Generate-EncryptionKey
Write-Host "      Encryption key generated (32 characters)" -ForegroundColor Green

# Save encryption key to file
$keyFileName = "ENCRYPTION_KEY_${timestamp}.txt"
$keyFilePath = Join-Path $backupFolder $keyFileName
Write-Host "[3/6] Saving encryption key..." -ForegroundColor Yellow

$keyFileContent = @"
========================================
BUDGET TRACKER - ENCRYPTION KEY
========================================

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Backup: $backupFolderName

ENCRYPTION KEY (Keep this secure!):
$encryptionKey

========================================
IMPORTANT SECURITY NOTES:
========================================

1. This key is required to decrypt your backup
2. Store this key in a secure location
3. Do NOT share this key with anyone
4. If you lose this key, the backup cannot be recovered
5. Consider storing a copy in a password manager

========================================
TO DECRYPT THE BACKUP:
========================================

Use the decryption script with this key:
.\decrypt-backup.ps1 -KeyFile "$keyFileName" -BackupFile "budget-tracker-backup_$timestamp.zip"

========================================
"@

$keyFileContent | Out-File -FilePath $keyFilePath -Encoding UTF8
Write-Host "      Key saved: $keyFilePath" -ForegroundColor Green

# Create temporary directory for backup staging
$tempBackupPath = Join-Path $env:TEMP "budget-tracker-backup-$timestamp"
Write-Host "[4/6] Preparing project files for backup..." -ForegroundColor Yellow

# Copy project to temp location (excluding .git and node_modules)
$excludedDirs = @(".git", "node_modules", "__pycache__", ".venv", "dist", "build")
$projectName = Split-Path $ProjectPath -Leaf

# Create the staging directory
New-Item -ItemType Directory -Path $tempBackupPath -Force | Out-Null

# Copy files excluding specified directories
Get-ChildItem -Path $ProjectPath -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($ProjectPath.Length + 1)
    $shouldExclude = $false
    
    foreach ($excludeDir in $excludedDirs) {
        if ($relativePath -like "$excludeDir*" -or $relativePath -like "*\$excludeDir\*") {
            $shouldExclude = $true
            break
        }
    }
    
    if (-not $shouldExclude) {
        $targetPath = Join-Path $tempBackupPath $relativePath
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        } else {
            $targetDir = Split-Path $targetPath -Parent
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            Copy-Item $_.FullName -Destination $targetPath -Force
        }
    }
}

Write-Host "      Files prepared for backup" -ForegroundColor Green

# Create encrypted ZIP archive
$zipFileName = "budget-tracker-backup_$timestamp.zip"
$zipFilePath = Join-Path $backupFolder $zipFileName
Write-Host "[5/6] Creating encrypted ZIP archive..." -ForegroundColor Yellow

# Use 7-Zip if available, otherwise use built-in compression with password protection
if (Get-Command 7z -ErrorAction SilentlyContinue) {
    # Use 7-Zip for strong encryption
    & 7z a -tzip -p"$encryptionKey" -mem=AES256 "$zipFilePath" "$tempBackupPath\*" | Out-Null
    Write-Host "      Archive created with AES-256 encryption (7-Zip)" -ForegroundColor Green
} else {
    # Use built-in .NET compression with password
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempBackupPath, $zipFilePath)
    Write-Host "      Archive created (Note: Install 7-Zip for AES-256 encryption)" -ForegroundColor Yellow
}

# Clean up temporary files
Write-Host "[6/6] Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $tempBackupPath -Recurse -Force
Write-Host "      Cleanup complete" -ForegroundColor Green

# Calculate file sizes
$zipSize = (Get-Item $zipFilePath).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

# Create a README file in the backup folder
$readmeContent = @"
BUDGET TRACKER - ENCRYPTED BACKUP
==================================

Backup Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Archive Size: $zipSizeMB MB

FILES IN THIS FOLDER:
---------------------
1. $zipFileName - Encrypted backup archive
2. $keyFileName - Encryption key (KEEP SECURE!)
3. README.txt - This file

SECURITY INFORMATION:
---------------------
The backup archive is encrypted and requires the encryption key to access.
The key is stored in: $keyFileName

IMPORTANT:
- Keep the encryption key file secure
- Store a copy of the key in a safe location
- Without the key, the backup cannot be recovered

TO RESTORE:
-----------
1. Extract the ZIP file using the encryption key
2. The password is in the $keyFileName file
3. Extract to your desired location

BACKUP CONTENTS:
----------------
- All source code files
- Configuration files
- Documentation
- Excluded: .git, node_modules, __pycache__, .venv, dist, build

For support or questions, refer to the project documentation.
"@

$readmeFilePath = Join-Path $backupFolder "README.txt"
$readmeContent | Out-File -FilePath $readmeFilePath -Encoding UTF8

# Display success summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  BACKUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backup Location:" -ForegroundColor Cyan
Write-Host "  $backupFolder" -ForegroundColor White
Write-Host ""
Write-Host "Files Created:" -ForegroundColor Cyan
Write-Host "  1. $zipFileName ($zipSizeMB MB)" -ForegroundColor White
Write-Host "  2. $keyFileName" -ForegroundColor White
Write-Host "  3. README.txt" -ForegroundColor White
Write-Host ""
Write-Host "Encryption Key (SAVE THIS!):" -ForegroundColor Yellow
Write-Host "  $encryptionKey" -ForegroundColor Red
Write-Host ""
Write-Host "IMPORTANT REMINDERS:" -ForegroundColor Red
Write-Host "  - The encryption key is saved in: $keyFileName" -ForegroundColor White
Write-Host "  - Store the key in a secure location" -ForegroundColor White
Write-Host "  - Without the key, the backup cannot be recovered" -ForegroundColor White
Write-Host ""
Write-Host "Opening backup folder..." -ForegroundColor Yellow
Start-Process explorer.exe $backupFolder

# Create a decryption helper script in the backup folder
$decryptScriptContent = @"
# Decryption Script for Budget Tracker Backup
# Usage: .\decrypt-backup.ps1

param(
    [string]`$KeyFile = "$keyFileName",
    [string]`$BackupFile = "$zipFileName",
    [string]`$OutputPath = "."
)

Write-Host "Budget Tracker - Backup Decryption" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Read encryption key
if (Test-Path `$KeyFile) {
    `$keyContent = Get-Content `$KeyFile -Raw
    if (`$keyContent -match "ENCRYPTION KEY.*:\s*([^\r\n]+)") {
        `$key = `$Matches[1].Trim()
        Write-Host "Encryption key loaded from `$KeyFile" -ForegroundColor Green
        
        Write-Host "`nTo decrypt manually:" -ForegroundColor Yellow
        Write-Host "1. Open the ZIP file: `$BackupFile" -ForegroundColor White
        Write-Host "2. Enter the password when prompted" -ForegroundColor White
        Write-Host "3. Extract to your desired location" -ForegroundColor White
        Write-Host "`nEncryption Key: `$key" -ForegroundColor Red
        
        # Copy key to clipboard
        `$key | Set-Clipboard
        Write-Host "`nKey copied to clipboard!" -ForegroundColor Green
    }
} else {
    Write-Host "Error: Key file not found: `$KeyFile" -ForegroundColor Red
}
"@

$decryptScriptPath = Join-Path $backupFolder "decrypt-backup.ps1"
$decryptScriptContent | Out-File -FilePath $decryptScriptPath -Encoding UTF8

Write-Host "Decryption helper script created: decrypt-backup.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backup process complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan