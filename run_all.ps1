# Perimeter & BharatPay Unified One-Click Launcher (PowerShell)
# Launches all 4 microservices in separate windows and opens the dashboards in your browser.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting Perimeter (ASPM) & BharatPay Platform        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RepoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }

# 1. Stop conflicting Docker containers if running
Write-Host "[1/5] Stopping any conflicting Docker containers on Port 8000..." -ForegroundColor Yellow
docker stop bharatpay-backend bharatpay-frontend bharatpay-gateway 2>$null | Out-Null

# 2. Terminal 1: BharatPay Backend (Port 8001)
Write-Host "[2/5] Launching BharatPay Banking Backend (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\frontend\bharatpay\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"

Start-Sleep -Seconds 2

# 3. Terminal 2: Perimeter ASPM Security Gateway (Port 8000)
Write-Host "[3/5] Launching Perimeter Security Gateway (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot'; python -m uvicorn person1_api_discovery.app.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# 4. Terminal 3: Perimeter SOC Console (Port 3000)
Write-Host "[4/5] Launching Perimeter SOC Console (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\frontend\dashboard'; npm run dev"

Start-Sleep -Seconds 2

# 5. Terminal 4: BharatPay Customer Web Portal (Port 5173)
Write-Host "[5/5] Launching BharatPay Customer Web Portal (Port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\frontend\bharatpay\frontend'; npm run dev"

Start-Sleep -Seconds 3

# Open consoles in default web browser
Write-Host "`nAll 4 services launched successfully!" -ForegroundColor Cyan
Write-Host "  * Perimeter SOC Console:     http://localhost:3000" -ForegroundColor White
Write-Host "  * Perimeter Evaluation:      http://localhost:3000/evaluation" -ForegroundColor White
Write-Host "  * Perimeter Gateway Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * BharatPay Customer Portal: http://localhost:5173" -ForegroundColor White
Write-Host "  * BharatPay Backend Docs:    http://localhost:8001/docs" -ForegroundColor White

Start-Process "http://localhost:3000"
Start-Process "http://localhost:5173"

