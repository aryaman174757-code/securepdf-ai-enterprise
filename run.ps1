# SecurePDF AI v3.0 - PowerShell Bootstrap Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " SECUREPDF AI v3.0 - Enterprise Zero-Trust Architecture" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n[1/3] Verifying Project Architecture..." -ForegroundColor Yellow
$dirs = @("backend", "frontend", "workers", "gateway", "docker", "tests", "docs")
foreach ($d in $dirs) {
    $p = Join-Path $root $d
    if (Test-Path $p) {
        Write-Host "  [+] $d/ verified" -ForegroundColor Green
    } else {
        Write-Host "  [-] $d/ missing" -ForegroundColor Red
    }
}

Write-Host "`n[2/3] Checking Docker Compose Configuration..." -ForegroundColor Yellow
$composeFile = Join-Path $root "docker\docker-compose.yml"
if (Test-Path $composeFile) {
    Write-Host "  [+] docker-compose.yml located" -ForegroundColor Green
}

Write-Host "`n[3/3] Ready to Launch!" -ForegroundColor Yellow
Write-Host "To launch complete platform with Docker:" -ForegroundColor White
Write-Host "  cd docker; docker compose up -d --build" -ForegroundColor Cyan
Write-Host "`nTo run backend standalone:" -ForegroundColor White
Write-Host "  cd backend; uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "`nTo run frontend standalone:" -ForegroundColor White
Write-Host "  cd frontend; npm run dev" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
