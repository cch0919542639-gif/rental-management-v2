$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Starting Flask dev server for rental rebuild..." -ForegroundColor Cyan
python -m flask --app app.wsgi run --debug
