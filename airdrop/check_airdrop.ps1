Write-Host '=== AIRDROP CHECK START ==='

Write-Host 'Python version:' (python --version)
Write-Host 'Virtualenv:' C:\Users\USER\Desktop\airdrop-main\airdrop-main\airdrop\venv

# Check DB file
\./test.db = './test.db'
if (Test-Path \./test.db) { Write-Host 'DB exists' } else { Write-Host 'DB missing, will create automatically' }

Write-Host '=== AIRDROP CHECK END ==='
