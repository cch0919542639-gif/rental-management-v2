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

py -3 .\scripts\run_production.py
