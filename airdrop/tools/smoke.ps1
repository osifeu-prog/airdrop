param(
  [string]$ProjectId = "airdrop_telegram_platform"
)

function Assert-Here([string]$ExpectedId){
  if (-not (Test-Path .\.project_id)) { throw "No .project_id here. WRONG FOLDER: $((Get-Location).Path)" }
  $id=(Get-Content .\.project_id -Raw).Trim()
  if ($id -ne $ExpectedId) { throw "WRONG PROJECT! id=$id expected=$ExpectedId PWD=$((Get-Location).Path)" }
}

$ErrorActionPreference="Stop"
Assert-Here $ProjectId

.\tools\setenv.ps1 | Out-Null
$env:DISABLE_RATE_LIMIT="1"

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
$listener.Start(); $port = ($listener.LocalEndpoint).Port; $listener.Stop()
$port | Set-Content -Encoding ascii -NoNewline ".\.run_port.txt"

$logOut=".\_smoke_$port.out.log"
$logErr=".\_smoke_$port.err.log"

$proc = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","$port","--log-level","debug") `
  -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru

try {
  $base="http://127.0.0.1:$port"

  $ok=$false
  for($i=0;$i -lt 60;$i++){
    $code = (curl.exe -s -o NUL -w "%{http_code}" "$base/health")
    if ($code -eq "200") { $ok=$true; break }
    Start-Sleep -Milliseconds 200
  }
  if(-not $ok){ throw "Server didn't become healthy. See $logOut / $logErr" }

  $count = & .\.venv\Scripts\python.exe -c "from app.main import app; print(len([r for r in app.routes if getattr(r,'path','')=='/api/v1/admin/whoami']))"
  if([int]$count -ne 1){ throw "whoami route count != 1 (got $count). Check router.py" }

  curl.exe -s -i "$base/health"
  curl.exe -s -i "$base/ready" 2>$null

  $adminSecret = (& .\.venv\Scripts\python.exe -c "from app.core.config import settings; print(getattr(settings,'ADMIN_SECRET',''))").Trim()
  curl.exe -s -i "$base/api/v1/admin/whoami" -H ("X-Admin-Secret: {0}" -f $adminSecret)

  Write-Host "SMOKE OK ✅  port=$port  out=$logOut  err=$logErr" -ForegroundColor Green
}
finally {
  if($proc -and -not $proc.HasExited){
    Stop-Process -Id $proc.Id -Force
  }
}