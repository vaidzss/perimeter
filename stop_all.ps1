# Stop all Perimeter & BharatPay services cleanly
Write-Host "Stopping Perimeter & BharatPay services..." -ForegroundColor Yellow

$ports = @(8000, 8001, 3000, 5173)
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns.OwningProcess | Select-Object -Unique
        foreach ($p in $pids) {
            if ($p -gt 0) {
                Write-Host "Stopping PID $p on Port $port..." -ForegroundColor Gray
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host "All services stopped." -ForegroundColor Green
