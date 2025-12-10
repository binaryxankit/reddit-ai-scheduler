# Start Reddit Mastermind Server
Write-Host "Starting Reddit Mastermind Server..." -ForegroundColor Green

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Start uvicorn server
Write-Host "Server starting at http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn main:app --reload --host 127.0.0.1 --port 8000

