# DraftKings Roster Optimizer - PowerShell Script
# This script runs the roster optimizer with configurable parameters

param(
    [string]$PlayersFile = "DKSalaries (10).csv",
    [string]$ConfigFile = "position_config.json",
    [int]$MaxSalary = 50000,
    [string]$DKOutput = "optimized_dk_output.csv",
    [string]$ReadableOutput = "optimized_summary.csv"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DraftKings Roster Optimizer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7 or higher" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if needed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -m pip install -q pandas pulp

# Display parameters
Write-Host ""
Write-Host "Parameters:" -ForegroundColor Cyan
Write-Host "  Players File: $PlayersFile"
Write-Host "  Config File: $ConfigFile"
Write-Host "  Max Salary: `$$MaxSalary"
Write-Host "  DK Output: $DKOutput"
Write-Host "  Readable Output: $ReadableOutput"
Write-Host ""

# Run the optimizer
Write-Host "Running optimizer..." -ForegroundColor Yellow
Write-Host ""

python optimize_roster.py `
  --players $PlayersFile `
  --config $ConfigFile `
  --max-salary $MaxSalary `
  --dk-output $DKOutput `
  --readable-output $ReadableOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Optimization complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output files:" -ForegroundColor Cyan
    Write-Host "  - $DKOutput (for DraftKings import)" -ForegroundColor White
    Write-Host "  - $ReadableOutput (human-readable)" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Optimization failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
