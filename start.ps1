# Multi-Agent Research Assistant — Start Script
# Usage: .\start.ps1

$root = $PSScriptRoot
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Multi-Agent Research Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start backend
Write-Host "[1/2] Starting backend (port 8000)..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "$root\backend\.venv\Scripts\uvicorn.exe" `
    -ArgumentList "main:app", "--port", "8000" `
    -WorkingDirectory "$root\backend" `
    -PassThru -WindowStyle Minimized
Write-Host "      Backend PID: $($backend.Id)" -ForegroundColor Green

Start-Sleep -Seconds 2

# Start frontend
Write-Host "[2/2] Starting frontend (port 5173)..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run", "dev" `
    -WorkingDirectory "$root\frontend" `
    -PassThru -WindowStyle Minimized
Write-Host "      Frontend PID: $($frontend.Id)" -ForegroundColor Green

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  App is running!" -ForegroundColor Green
Write-Host "  Open: http://localhost:5173" -ForegroundColor Green
Write-Host "  API:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to STOP both services..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "Stopping services..." -ForegroundColor Red
Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
Stop-Process -Id $frontend.Id -ErrorAction SilentlyContinue
Write-Host "Done."
