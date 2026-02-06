Write-Host "PYTHON CHECK" -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
} catch {
    throw "Python is not installed or not in PATH"
}

Write-Host "Detected Python version: $pythonVersion"

$versionNumber = ($pythonVersion -split " ")[1]
if ([version]$versionNumber -lt [version]"3.10") {
    throw "Python version must be 3.10 or higher"
}

Write-Host "PYTHON CHECK PASSED" -ForegroundColor Green
