param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000
)

if (-not $env:APP_ENV) {
    $env:APP_ENV = "production"
}

$env:APP_HOST = $Host
$env:APP_PORT = "$Port"

if (-not $env:SECRET_KEY) {
    throw "SECRET_KEY is required for production mode."
}

if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required for production mode."
}

if ($env:DATABASE_URL -like "sqlite*") {
    throw "SQLite DATABASE_URL is not allowed for Phase 5 production mode. Use PostgreSQL."
}

py -3 .\scripts\run_production.py
