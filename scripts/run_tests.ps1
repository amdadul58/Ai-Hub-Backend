$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Project virtual environment not found: $Python"
    exit 1
}

Write-Host "AI Hub Backend - Running test suite" -ForegroundColor Cyan
& $Python -m pytest -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Review the output above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "All tests passed." -ForegroundColor Green