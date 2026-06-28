$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "[seed/reset/check] Safe preflight for rental rebuild" -ForegroundColor Cyan

function Run-Seed {
    Write-Host "Running seed_demo_data.py ..." -ForegroundColor Cyan
    python .\scripts\seed_demo_data.py
}

function Run-IntegrationCheck {
    Write-Host "Running integration tests (pytest tests\\integration -q) ..." -ForegroundColor Cyan
    pytest tests\integration -q
}

# Lightweight option parsing (no destructive behavior)
$mode = "all"
if ($args.Count -gt 0) {
    $mode = $args[0].ToLower()
}

switch ($mode) {
    "seed" { Run-Seed }
    "check" { Run-IntegrationCheck }
    "all" { Run-Seed; Run-IntegrationCheck }
    default {
        Write-Host "Unknown mode: $mode" -ForegroundColor Yellow
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\\scripts\\seed_reset_check.ps1 [seed|check|all]" -ForegroundColor Yellow
        exit 2
    }
}

Write-Host "Done." -ForegroundColor Green

