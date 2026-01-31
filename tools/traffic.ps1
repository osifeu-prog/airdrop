param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("start","stop","status","health","logs")]
  [string]$cmd
)

$ErrorActionPreference="Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path) | Out-Null
Set-Location ".."  # repo root

$Port = 18082
$HostAddr = "127.0.0.1"
$PidFile = ".\.server_pid"

function Get-ListenerPid([int]$port) {
  $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($c) { return [int]$c.OwningProcess }
  return $null
}

function Ensure-Env() {
  Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
  Remove-Item Env:REDIS_URL -ErrorAction SilentlyContinue
  Remove-Item Env:TELEGRAM_TOKEN -ErrorAction SilentlyContinue
  Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

  $env:PYTHONPATH = (Join-Path (Get-Location) "backend")
  $env:PORT = "$Port"
}

switch ($cmd) {

  "status" {
    $listenerPid = Get-ListenerPid $Port
    if ($listenerPid) {
      $p = Get-Process -Id $listenerPid -ErrorAction SilentlyContinue
      if ($p) {
        Write-Host "RUNNING  http://$HostAddr`:$Port  PID=$listenerPid  ($($p.ProcessName))"
        exit 0
      }
    }
    Write-Host "STOPPED  port $Port is free"
    exit 1
  }

  "health" {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -Uri "http://$HostAddr`:$Port/health" -TimeoutSec 3
      Write-Host "HEALTH OK  $($r.StatusCode)  $($r.Content)"
      exit 0
    } catch {
      Write-Host "HEALTH FAIL  $($_.Exception.Message)"
      exit 2
    }
  }

  "start" {
    $listenerPid = Get-ListenerPid $Port
    if ($listenerPid) {
      Write-Host "Already running on port $Port (PID=$listenerPid)."
      exit 0
    }

    Ensure-Env

    $args = "-m uvicorn app.main:app --host $HostAddr --port $Port --log-level info"
    $proc = Start-Process -FilePath "python" -ArgumentList $args -WorkingDirectory (Get-Location).Path -PassThru
    $proc.Id | Set-Content -Encoding ascii $PidFile

    Start-Sleep -Milliseconds 700
    & $PSCommandPath status | Out-Null
    Write-Host "Started."
    exit 0
  }

  "stop" {
    $listenerPid = Get-ListenerPid $Port
    if (-not $listenerPid -and (Test-Path $PidFile)) {
      $listenerPid = [int](Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    }

    if ($listenerPid) {
      try {
        Stop-Process -Id $listenerPid -Force -ErrorAction Stop
        Write-Host "Stopped PID=$listenerPid"
      } catch {
        Write-Host "Stop attempted but failed: $($_.Exception.Message)"
      }
    } else {
      Write-Host "Nothing to stop (port $Port is free)."
    }

    Remove-Item $PidFile -ErrorAction SilentlyContinue
    exit 0
  }

  "logs" {
    Write-Host "Logs are printed to the server console. Use status/health for checks."
    exit 0
  }
}
