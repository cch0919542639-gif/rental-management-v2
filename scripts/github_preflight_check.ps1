$ErrorActionPreference = "Stop"

Write-Host "GitHub preflight check for rental rebuild" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$warningPatterns = @(
    ".env",
    ".env.*",
    "runtime.db",
    "*.db",
    "*.sqlite",
    "*.sqlite3"
)

$warningDirs = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    ".vscode",
    ".idea"
)

$foundWarnings = @()

foreach ($pattern in $warningPatterns) {
    $matches = Get-ChildItem -Path $repoRoot -Recurse -Force -File -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -like $pattern
    }
    foreach ($match in $matches) {
        $foundWarnings += "FILE: $($match.FullName)"
    }
}

foreach ($dirName in $warningDirs) {
    $matches = Get-ChildItem -Path $repoRoot -Recurse -Force -Directory -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -eq $dirName
    }
    foreach ($match in $matches) {
        $foundWarnings += "DIR:  $($match.FullName)"
    }
}

if ($foundWarnings.Count -eq 0) {
    Write-Host "No risky local files detected." -ForegroundColor Green
} else {
    Write-Host "Warnings detected:" -ForegroundColor Yellow
    $foundWarnings | Sort-Object -Unique | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Required GitHub files:" -ForegroundColor Cyan
$requiredFiles = @(
    ".gitignore",
    ".gitattributes",
    ".github\\PULL_REQUEST_TEMPLATE.md",
    "CONTRIBUTING.md",
    "COLLABORATION_RULES.md",
    "docs\\operations\\github-upload-checklist.md",
    "docs\\operations\\github-branch-and-pr-flow.md",
    "docs\\operations\\github-second-round-collaboration.md"
)

$missing = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path (Join-Path $repoRoot $file))) {
        $missing += $file
    }
}

if ($missing.Count -eq 0) {
    Write-Host "Required files are present." -ForegroundColor Green
} else {
    Write-Host "Missing required files:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    exit 1
}

Write-Host ""
Write-Host "Preflight complete." -ForegroundColor Green
