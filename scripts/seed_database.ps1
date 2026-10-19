$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
& ".\.venv\Scripts\python.exe" -c "from src.database.base import initialize_database; print(initialize_database())"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
