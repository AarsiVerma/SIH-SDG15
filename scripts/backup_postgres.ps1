<#
.SYNOPSIS
    PostgreSQL backup script for VANRAKSHA AI (Windows PowerShell)
#>

param(
    [string]$BackupDir = "C:\backups\vanraksha",
    [string]$ContainerName = "vanraksha-db-prod",
    [string]$DbName = "vanraksha",
    [string]$DbUser = "vanraksha"
)

$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "vanraksha_${date}.sql.gz"

Write-Host "[$(Get-Date)] Starting backup of $DbName..." -ForegroundColor Cyan

# Ensure backup directory exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# Run pg_dump in container
$pgDumpCmd = "pg_dump -U $DbUser -d $DbName --no-owner --no-privileges | gzip"
$fullCmd = "docker exec $ContainerName bash -c `"$pgDumpCmd`" > `"$backupFile`""

try {
    Invoke-Expression $fullCmd
    if (Test-Path $backupFile -and (Get-Item $backupFile).Length -gt 0) {
        Write-Host "[$(Get-Date)] Backup complete: $backupFile" -ForegroundColor Green
        Get-Item $backupFile | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
    } else {
        Write-Error "Backup file missing or empty!"
        exit 1
    }
} catch {
    Write-Error "Backup failed: $_"
    exit 1
}

# Retention: keep last 30 days
Write-Host "[$(Get-Date)] Cleaning old backups (>30 days)..." -ForegroundColor Cyan
$cutoff = (Get-Date).AddDays(-30)
Get-ChildItem $BackupDir -Filter "vanraksha_*.sql.gz" | Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force

Write-Host "[$(Get-Date)] Done." -ForegroundColor Green