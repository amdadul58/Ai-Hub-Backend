$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "AI Hub Backend - Environment Check" -ForegroundColor Cyan

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Project virtual environment not found." -ForegroundColor Yellow
    Write-Host "Create it with: py -3.12 -m venv .venv"
    exit 1
}

& $Python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python environment check failed."
}

if (-not (Test-Path "requirements.txt")) {
    throw "requirements.txt was not found."
}

Write-Host "Checking installed project dependencies..." -ForegroundColor Cyan
& $Python -m pip check
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency check reported an issue. Review it before installing packages." -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Write-Host "Environment check completed. No packages or model weights were downloaded." -ForegroundColor Green
