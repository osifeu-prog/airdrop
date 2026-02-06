$ErrorActionPreference = "Stop"
$ROOT = (Get-Location).Path

# Allow importing both: app.* (from backend) and bot.* (from repo root)
$env:PYTHONPATH = "$ROOT;$ROOT\backend"

Write-Host "[env] PYTHONPATH=$env:PYTHONPATH"