param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start","stop","status","test","doctor")]
    [string]$Action
)

$Server = "http://127.0.0.1:8000"
$PidFile = ".airdrop.pid"
$LogDir = "logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Name $LogDir }

function Start-Server {
    if (Test-Path $PidFile) {
        Write-Host "[!] Server already running (PID exists)"
        return
    }

    Write-Host "[*] Starting Airdrop server..."
    $env:PYTHONPATH = "$PWD\backend"

    $proc = Start-Process python `
        "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > logs\server.log 2>&1" `
        -PassThru -WindowStyle Hidden

    $proc.Id | Out-File $PidFile -Encoding ASCII
    Start-Sleep 3
    Write-Host "[OK] Server started (PID $($proc.Id))"
}

function Stop-Server {
    if (!(Test-Path $PidFile)) {
        Write-Host "[!] Server not running"
        return
    }

    $serverPid = Get-Content $PidFile
    if (Get-Process -Id $serverPid -ErrorAction SilentlyContinue) {
        Stop-Process -Id $serverPid -Force
        Write-Host "[OK] Server stopped (PID $serverPid)"
    } else {
        Write-Host "[!] PID file exists but process not running"
    }

    Remove-Item $PidFile -Force
}

function Status-Server {
    if (Test-Path $PidFile) {
        $serverPid = Get-Content $PidFile
        if (Get-Process -Id $serverPid -ErrorAction SilentlyContinue) {
            Write-Host "[OK] Server running (PID $serverPid)"
        } else {
            Write-Host "[!] PID file exists but process not running"
        }
    } else {
        Write-Host "[!] Server stopped"
    }
}

function Test-Server {
    Write-Host "[*] Running system tests..."
    $failed = $false

    try {
        $health = Invoke-RestMethod "$Server/health" -TimeoutSec 3
        if ($health.status -ne "ok") {
            Write-Host "[X] Health check failed"
            $failed = $true
        } else {
            Write-Host "[OK] Health check passed"
        }
    } catch {
        Write-Host "[X] Health endpoint unreachable"
        $failed = $true
    }

    try {
        $ready = Invoke-RestMethod "$Server/ready" -TimeoutSec 3
        Write-Host "[OK] Ready endpoint reachable (db=$($ready.db), redis=$($ready.redis))"
    } catch {
        Write-Host "[X] Ready endpoint failed"
        $failed = $true
    }

    try {
        Invoke-RestMethod "$Server/openapi.json" -TimeoutSec 3 | Out-Null
        Write-Host "[OK] OpenAPI available"
    } catch {
        Write-Host "[X] OpenAPI missing"
        $failed = $true
    }

    if ($failed) {
        Write-Host "[FAIL] System test failed"
        exit 1
    } else {
        Write-Host "[PASS] All system tests passed"
        exit 0
    }
}

function Doctor-Server {
    Write-Host "[*] Running environment diagnostics..."
    $issues = @()

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $issues += "Python not found" }
    if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) { $issues += "Uvicorn not installed" }
    if (-not (Test-Path $LogDir)) { $issues += "Logs directory missing" }
    if (!(Test-Path $PidFile)) { Write-Host "[*] PID file not present (ok)"} else { Write-Host "[*] PID file exists" }

    if ($issues.Count -eq 0) {
        Write-Host "[OK] Environment looks good"
    } else {
        Write-Host "[X] Issues detected:"
        $issues | ForEach-Object { Write-Host "  - $_" }
    }
}

switch ($Action) {
    "start" { Start-Server }
    "stop" { Stop-Server }
    "status" { Status-Server }
    "test" { Test-Server }
    "doctor" { Doctor-Server }
}
