$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1

Write-Host "[1/3] Alembic downgrade base" -ForegroundColor Cyan
$env:PYTHONPATH = "."
alembic -c migrations\alembic.ini downgrade base

Write-Host "[2/3] Alembic upgrade head" -ForegroundColor Cyan
alembic -c migrations\alembic.ini upgrade head

Write-Host "[3/3] Done" -ForegroundColor Green
