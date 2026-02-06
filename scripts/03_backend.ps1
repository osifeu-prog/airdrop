Write-Host "STARTING BACKEND" -ForegroundColor Cyan

$backendPath = Join-Path $PSScriptRoot "..\backend"
Set-Location $backendPath

# Install requirements
pip install -r ..\requirements.txt

# Run backend
Start-Process python -ArgumentList "main.py" -NoNewWindow

Write-Host "BACKEND RUNNING" -ForegroundColor Green
