Write-Host "SYSTEM HEALTHCHECK" -ForegroundColor Cyan

$backendRunning = Get-Process -Name python -ErrorAction SilentlyContinue
if ($backendRunning) {
    Write-Host "Python processes detected: $($backendRunning.Count)"
} else {
    Write-Host "No Python processes running. Backend/Bot may not be running!" -ForegroundColor Red
}

Write-Host "HEALTHCHECK COMPLETE" -ForegroundColor Green
