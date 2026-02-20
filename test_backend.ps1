# Test Backend Connection
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -UseBasicParsing
    Write-Host "✓ Backend is ONLINE - Status: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "✗ Backend check failed: $_"
    Write-Host "Make sure backend is running: cd backend; .\.venv\Scripts\activate; uvicorn app.main:app --host 127.0.0.1 --port 8000"
}


