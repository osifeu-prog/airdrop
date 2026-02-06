Write-Host "AIRDROP SYSTEM BOOTSTRAP" -ForegroundColor Cyan
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$scripts = @(
    "scripts/00_env_check.ps1",
    "scripts/01_python_check.ps1",
    "scripts/02_venv.ps1",
    "scripts/03_backend.ps1",
    "scripts/04_bot.ps1",
    "scripts/99_healthcheck.ps1"
)

foreach ($s in $scripts) {
    Write-Host "`nRunning $s" -ForegroundColor Yellow
    if (!(Test-Path $s)) {
        throw "Missing script: $s"
    }
    . $s
}

Write-Host "`nAIRDROP SYSTEM READY" -ForegroundColor Green
