#!/bin/bash
# Railway Test Script

echo "🚀 Starting Railway deployment test..."

# Check Python version
echo "Python version:"
python --version

# Check dependencies
echo "Checking dependencies..."
pip list | grep -E "(fastapi|uvicorn|telegram|requests|pydantic)"

# Test API
echo "Testing API..."
if command -v curl &> /dev/null; then
    curl -f http://localhost:8000/health || echo "Health check failed"
    curl -f http://localhost:8000/ || echo "Root endpoint failed"
else
    echo "curl not found, using python..."
    python -c "
import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    print(f'Health: {r.status_code} - {r.text}')
except Exception as e:
    print(f'Health check error: {e}')
    
try:
    r = requests.get('http://localhost:8000/', timeout=5)
    print(f'Root: {r.status_code} - {r.text[:100]}...')
except Exception as e:
    print(f'Root endpoint error: {e}')
"
fi

echo "✅ Test completed!"
