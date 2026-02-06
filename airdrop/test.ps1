$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1

Write-Host "[1/2] Running unit tests (pytest)" -ForegroundColor Cyan
pytest -q

Write-Host "[2/2] Done" -ForegroundColor Green
