Write-Host "?? AIRDROP SYSTEM BOOT"

# 1. בדיקת Python
Write-Host "`n?? Checking Python..."
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "? Python not available"
    exit 1
}

# 2. בדיקת תיקיית backend
if (!(Test-Path "backend\app\main_run.py")) {
    Write-Host "? main_run.py missing"
    exit 1
}

# 3. הפעלת השרת
Write-Host "`n?? Starting FastAPI server..."
Start-Process powershell -ArgumentList `
    "python -m uvicorn backend.app.main_run:app --reload"

Start-Sleep -Seconds 3

# 4. בדיקת API
Write-Host "`n?? Testing API..."
try {
    $ping = Invoke-RestMethod http://127.0.0.1:8000/public/ping -TimeoutSec 3
    Write-Host "? API OK:" ($ping | ConvertTo-Json)
} catch {
    Write-Host "? API failed to respond"
}

Write-Host "`n?? System is UP"
