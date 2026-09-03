<# 
.SYNOPSIS
    VANRAKSHA AI development helper (PowerShell).
#>

param(
    [switch]$Help,
    [ValidateSet("dev","test","migrate","lint","seed")] $Command = "dev"
)

if ($Help) {
    Write-Host "Usage: .\scripts\dev.ps1 [-Command dev|test|migrate|lint|seed]"
    exit 0
}

$projectRoot = Split-Path -Parent $PSScriptRoot

switch ($Command) {
    "dev" {
        Write-Host "Starting VANRAKSHA stack..." -ForegroundColor Green
        docker compose -f "$projectRoot\docker-compose.yml" up --build
    }
    "test" {
        Write-Host "Running backend tests..." -ForegroundColor Green
        docker compose -f "$projectRoot\docker-compose.yml" run --rm api python -m pytest backend/tests -q
    }
    "migrate" {
        Write-Host "Running migrations..." -ForegroundColor Green
        docker compose -f "$projectRoot\docker-compose.yml" run --rm api alembic -c backend/alembic.ini upgrade head
    }
    "lint" {
        Write-Host "Linting..." -ForegroundColor Green
        docker compose -f "$projectRoot\docker-compose.yml" run --rm api python -m ruff check backend/app
    }
    "seed" {
        Write-Host "Seeding demo data..." -ForegroundColor Green
        docker compose -f "$projectRoot\docker-compose.yml" run --rm api python scripts/seed_demo.py
    }
    default {
        Write-Error "Unknown command: $Command"
        exit 1
    }
}