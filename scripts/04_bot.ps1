Write-Host "STARTING BOT" -ForegroundColor Cyan

$botPath = Join-Path $PSScriptRoot "..\bot"
Set-Location $botPath

# Run bot
Start-Process python -ArgumentList "bot.py" -NoNewWindow

Write-Host "BOT RUNNING" -ForegroundColor Green
