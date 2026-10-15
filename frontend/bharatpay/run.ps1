# BharatPay Windows Development Launcher
Write-Host "=== Starting BharatPay in Development Mode ===" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Backend setup
$VenvPython = Join-Path $ScriptDir "backend\venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[Dev] Creating Python virtual environment in backend\venv..." -ForegroundColor Yellow
    python -m venv (Join-Path $ScriptDir "backend\venv")
    & (Join-Path $ScriptDir "backend\venv\Scripts\pip.exe") install --upgrade pip
    & (Join-Path $ScriptDir "backend\venv\Scripts\pip.exe") install -r (Join-Path $ScriptDir "backend\requirements.txt")
}

Write-Host "[Dev] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$BackendProcess = Start-Process -FilePath $VenvPython -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory (Join-Path $ScriptDir "backend") -PassThru

Write-Host "[Dev] Starting React Vite Frontend on http://localhost:5173..." -ForegroundColor Green
$FrontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory (Join-Path $ScriptDir "frontend") -PassThru

Write-Host "BharatPay is running!" -ForegroundColor Cyan
Write-Host "- Backend:  http://localhost:8000"
Write-Host "- Frontend: http://localhost:5173"
Write-Host "Press Ctrl+C or close this window to exit."

try {
    Wait-Process -Id $BackendProcess.Id, $FrontendProcess.Id
} finally {
    Stop-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $FrontendProcess.Id -ErrorAction SilentlyContinue
}
