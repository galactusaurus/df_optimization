@echo off
REM DraftKings Roster Optimizer - Windows Batch Script
REM This script runs the roster optimizer with default parameters

echo ========================================
echo DraftKings Roster Optimizer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -m pip install -q pandas pulp

echo.
echo Running optimizer...
echo.

REM Run the optimizer with default files
python optimize_roster.py ^
  --players "DKSalaries (10).csv" ^
  --config position_config.json ^
  --max-salary 50000 ^
  --dk-output optimized_dk_output.csv ^
  --readable-output optimized_summary.csv

echo.
echo ========================================
echo Optimization complete!
echo.
echo Output files:
echo   - optimized_dk_output.csv (for DraftKings import)
echo   - optimized_summary.csv (human-readable)
echo ========================================
echo.

pause
