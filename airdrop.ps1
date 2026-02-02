param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start","stop","test","status")]
    [string]$Action
)

$Server = "http://127.0.0.1:8000"
$PidFile = ".airdrop.pid"

function Start-Server {
    if (Test-Path $PidFile) {
        Write-Host "[!] Server already running"
        return
    }

    Write-Host "[*] Starting Airdrop server..."

    $env:PYTHONPATH = "$PWD\backend"

    $proc = Start-Process python `
        "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > logs\\server.log 2>&1" `
        -PassThru `
        -WindowStyle Hidden

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
    Stop-Process -Id $serverPid -Force
    Remove-Item $PidFile

    Write-Host "[OK] Server stopped (PID $serverPid)"
}

function Test-Server {
    Write-Host "[*] Testing server..."

    try {
        Invoke-RestMethod "$Server/health" -TimeoutSec 3 | Out-Null
        Invoke-RestMethod "$Server/openapi.json" -TimeoutSec 3 | Out-Null
        Write-Host "[OK] All checks passed"
    } catch {
        Write-Host "[X] Test failed"
    }
}

function Status-Server {
    if (Test-Path $PidFile) {
        $serverPid = Get-Content $PidFile
        Write-Host "[OK] Server running (PID $serverPid)"
    } else {
        Write-Host "[!] Server stopped"
    }
}

switch ($Action) {
    "start"  { Start-Server }
    "stop"   { Stop-Server }
    "test"   { Test-Server }
    "status" { Status-Server }
}
