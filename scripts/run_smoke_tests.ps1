$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Running integration smoke tests..." -ForegroundColor Cyan
pytest tests\integration -q
