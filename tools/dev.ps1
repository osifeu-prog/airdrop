param(
  [string]$BindHost = "127.0.0.1",
  [switch]$NoReload
)

$ErrorActionPreference = "Stop"

function Get-FreePort {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  $listener.Start()
  $p = ($listener.LocalEndpoint).Port
  $listener.Stop()
  return $p
}

function Wait-Http200([string]$url, [int]$timeoutMs = 12000) {
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  while ($sw.ElapsedMilliseconds -lt $timeoutMs) {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 -Uri $url
      if ($r.StatusCode -eq 200) { return $true }
    } catch {}
    Start-Sleep -Milliseconds 250
  }
  return $false
}

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ROOT

$setenv = Join-Path $ROOT "tools\setenv.ps1"
if (Test-Path $setenv) { & $setenv | Out-Null }
$env:DISABLE_RATE_LIMIT = "1"

$port = Get-FreePort
$port | Set-Content -Encoding ascii -NoNewline ".\.run_port.txt"

$base = "http://$BindHost`:$port"
Write-Host ""
Write-Host "[dev] Base URL: $base" -ForegroundColor Cyan
Write-Host "[dev] Swagger : $base/docs" -ForegroundColor Cyan
Write-Host "[dev] OpenAPI : $base/openapi.json" -ForegroundColor Cyan
Write-Host ""

$py = Join-Path $ROOT ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Missing venv python at $py" }

$uvArgs = @("-m","uvicorn","app.main:app","--host",$BindHost,"--port",$port,"--log-level","debug")
if (-not $NoReload) { $uvArgs += @("--reload") }

$job = Start-Job -ScriptBlock {
  param($baseUrl)
  function Wait-Http200([string]$url, [int]$timeoutMs = 12000) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $timeoutMs) {
      try {
        $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 -Uri $url
        if ($r.StatusCode -eq 200) { return $true }
      } catch {}
      Start-Sleep -Milliseconds 250
    }
    return $false
  }
  [pscustomobject]@{
    health   = Wait-Http200 "$baseUrl/health"
    ready    = Wait-Http200 "$baseUrl/ready"
    progress = Wait-Http200 "$baseUrl/api/v1/public/progress"
    base     = $baseUrl
  }
} -ArgumentList $base

try {
  & $py @uvArgs
} finally {
  try {
    $res = Receive-Job $job -Wait -AutoRemoveJob
    Write-Host ""
    Write-Host "[smoke] /health                : $($res.health)" -ForegroundColor Yellow
    Write-Host "[smoke] /ready                 : $($res.ready)" -ForegroundColor Yellow
    Write-Host "[smoke] /api/v1/public/progress: $($res.progress)" -ForegroundColor Yellow
    Write-Host "[smoke] base                   : $($res.base)" -ForegroundColor Yellow
    Write-Host ""
  } catch {}
}