$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

$env:PYTHONPATH = (Join-Path (Get-Location) "backend")
$env:ENVIRONMENT = "local"
$env:PORT = "18082"
$env:DB_DISABLED = "1"
$env:REDIS_DISABLED = "1"

$port = 18082
$c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($c) {
  Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
}

python -m uvicorn app.main:app --host 127.0.0.1 --port 18082 --log-level info
