$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

$env:PYTHONPATH = (Join-Path (Get-Location) "backend")
$env:PORT="18082"

# enable DB/Redis (unset disables)
Remove-Item Env:DB_DISABLED -ErrorAction SilentlyContinue
Remove-Item Env:REDIS_DISABLED -ErrorAction SilentlyContinue

# load .env if exists (repo root)
if (Test-Path ".\.env") {
  Get-Content ".\.env" | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $kv = $_ -split '=',2
    if ($kv.Count -eq 2) {
      $k=$kv[0].Trim()
      $v=$kv[1].Trim()
      if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v=$v.Substring(1,$v.Length-2) }
      if ($v.StartsWith("'") -and $v.EndsWith("'")) { $v=$v.Substring(1,$v.Length-2) }
      Set-Item -Path "Env:$k" -Value $v
    }
  }
}

# free port if taken
$port = 18082
$c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($c) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }

python -m uvicorn app.main:app --host 127.0.0.1 --port 18082 --log-level info
