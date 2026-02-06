$ErrorActionPreference = "Stop"
. "$PSScriptRoot\tools\setenv.ps1"
if (!(Test-Path .\.venv)) { throw "Missing .venv. Run .\setup.ps1 first." }

Write-Host "[1/2] Running Alembic upgrade head"
& .\.venv\Scripts\python.exe -m alembic -c .\alembic.ini upgrade head

Write-Host "[2/2] Done"