$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

# clean isolation
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
Remove-Item Env:DB_DISABLED -ErrorAction SilentlyContinue

$env:PYTHONPATH = (Join-Path (Get-Location) "backend")
$env:PORT="18081"

if (-not $env:DATABASE_URL) {
  Write-Host "ERROR: DATABASE_URL is not set. Paste it first:" -ForegroundColor Red
  Write-Host '$env:DATABASE_URL="postgresql+psycopg2://USER:PASS@HOST:PORT/DBNAME"' -ForegroundColor Yellow
  exit 1
}

python -m uvicorn app.main:app --host 127.0.0.1 --port 18081 --log-level info
