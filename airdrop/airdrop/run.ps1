.\tools\setenv.ps1

# --- dynamic ports ---
$BACKEND_PORT = if ($env:PORT) { [int]$env:PORT } else { 8000 }
Write-Host "[conf] BACKEND_PORT=$BACKEND_PORT"

Write-Host "[1/4] Starting backend (Uvicorn) on http://127.0.0.1:$BACKEND_PORT"
$backend = Start-Process -PassThru -NoNewWindow -FilePath ".\.venv\Scripts\python.exe" -ArgumentList @(
  "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","$BACKEND_PORT","--reload"
) -WorkingDirectory ".\backend"

Write-Host "[2/4] Starting worker (auto-approve queue)"
$worker = Start-Process -PassThru -NoNewWindow -FilePath ".\.venv\Scripts\python.exe" -ArgumentList @(
  "-m","app.worker"
) -WorkingDirectory ".\backend"

Write-Host "[3/4] Starting bot (long polling by default)"
$bot = Start-Process -PassThru -NoNewWindow -FilePath ".\.venv\Scripts\python.exe" -ArgumentList @(
  "-m","bot.main"
) -WorkingDirectory "."

Write-Host "[4/4] Running. Press Enter to stop all..."
[void][System.Console]::ReadLine()

foreach ($p in @($bot,$worker,$backend)) {
  try { if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force } } catch {}
}