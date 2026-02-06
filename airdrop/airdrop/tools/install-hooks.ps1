$ErrorActionPreference = "Stop"
Write-Host "[1/2] Configuring git hooks path to .githooks" -ForegroundColor Cyan
git config core.hooksPath .githooks
Write-Host "[2/2] Done. (Hooks are now active for this repo)" -ForegroundColor Green
