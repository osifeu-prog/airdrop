Write-Host "ENVIRONMENT CHECK" -ForegroundColor Cyan

$required = @(
    ".env.example",
    "requirements.txt",
    "bot",
    "backend"
)

foreach ($item in $required) {
    if (!(Test-Path (Join-Path $PSScriptRoot "..\$item"))) {
        throw "Missing required item: $item"
    }
    Write-Host "Found $item"
}

Write-Host "ENV CHECK PASSED" -ForegroundColor Green
