$ErrorActionPreference = "Stop"

Write-Host "[1/5] Creating venv (.venv)" -ForegroundColor Cyan
if (!(Test-Path ".\.venv")) {
  python -m venv .venv
}

Write-Host "[2/5] Activating venv" -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1

Write-Host "[3/5] Upgrading pip" -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "[4/5] Installing requirements" -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "[5/5] Done" -ForegroundColor Green
