# FOP Developer Toolkit
# Save this file as: C:\Users\Adam\Documents\Projects\fms-platform\fop-dev.ps1
# Then dot-source it in PowerShell:
# . "C:\Users\Adam\Documents\Projects\fms-platform\fop-dev.ps1"

$global:FOP_ROOT = "C:\Users\Adam\Documents\Projects\fms-platform"
$global:FOP_BACKEND = Join-Path $FOP_ROOT "backend"
$global:FOP_FRONTEND = Join-Path $FOP_ROOT "frontend"

function fop-root {
    Set-Location $global:FOP_ROOT
}

function fop-backend {
    Set-Location $global:FOP_BACKEND
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        . .\.venv\Scripts\Activate.ps1
    } else {
        Write-Host "Backend virtual environment not found at .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    }
}

function fop-frontend {
    Set-Location $global:FOP_FRONTEND
}

function fop-migrate {
    fop-backend
    alembic upgrade head
}

function fop-seed-soho {
    fop-backend
    python -m scripts.seed_soho_phase1_property
}

function fop-clean-soho {
    fop-backend
    python -m scripts.seed_soho_phase1_property --cleanup-soho
}

function fop-backend-run {
    fop-backend
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

function fop-frontend-run {
    fop-frontend
    npm run dev
}

function fop-typecheck {
    fop-frontend
    npm run typecheck
}

function fop-check {
    Write-Host "Running FOP checks..." -ForegroundColor Cyan

    fop-backend
    Write-Host "Checking backend import..." -ForegroundColor Cyan
    python -c "import app.main; print('Backend import OK')"

    Write-Host "Running migrations..." -ForegroundColor Cyan
    alembic upgrade head

    Write-Host "Running SOHO seed..." -ForegroundColor Cyan
    python -m scripts.seed_soho_phase1_property

    fop-frontend
    Write-Host "Running frontend typecheck..." -ForegroundColor Cyan
    npm run typecheck

    Write-Host "FOP checks complete." -ForegroundColor Green
}

function fop-open {
    Start-Process "http://localhost:8000/docs"
    Start-Process "http://localhost:3000"
    Start-Process "http://localhost:3000/buildings"
    Start-Process "http://localhost:3000/properties"
}

function fop-status {
    Write-Host "FOP Root:     $global:FOP_ROOT"
    Write-Host "Backend:      $global:FOP_BACKEND"
    Write-Host "Frontend:     $global:FOP_FRONTEND"
    Write-Host ""
    Write-Host "Key commands:"
    Write-Host "  fop-root"
    Write-Host "  fop-backend"
    Write-Host "  fop-frontend"
    Write-Host "  fop-migrate"
    Write-Host "  fop-seed-soho"
    Write-Host "  fop-clean-soho"
    Write-Host "  fop-backend-run"
    Write-Host "  fop-frontend-run"
    Write-Host "  fop-typecheck"
    Write-Host "  fop-check"
    Write-Host "  fop-open"
}

fop-status
