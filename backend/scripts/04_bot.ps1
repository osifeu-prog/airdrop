Write-Host "STARTING BOT" -ForegroundColor Cyan

$botPath = Join-Path $PSScriptRoot "..\bot"
Set-Location $botPath

# ודא שיש קובץ .env עם טוקן חוקי
if (!(Test-Path "..\.env")) {
    Write-Host "Missing .env file with your BOT TOKEN!" -ForegroundColor Red
    throw ".env file not found"
}

# Run bot
Start-Process python -ArgumentList "bot.py" -NoNewWindow

Write-Host "BOT RUNNING" -ForegroundColor Green
