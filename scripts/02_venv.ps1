Write-Host "VIRTUAL ENV SETUP" -ForegroundColor Cyan

$venvPath = Join-Path $PSScriptRoot "..\venv"

if (!(Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "Created virtual environment at $venvPath"
} else {
    Write-Host "Virtual environment already exists"
}

# Activate venv
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
Write-Host "Activating virtual environment..."
. $activate

Write-Host "VIRTUAL ENV READY" -ForegroundColor Green
