@echo off
REM reset_demo_data.bat
REM Phase 2 — Drop and re-seed demo data in one step.
REM
REM Usage:
REM     scripts\reset_demo_data.bat
REM
REM Note: This will DESTROY all existing data and recreate it.

echo =====================================================
echo   Resetting demo data — all existing data will be lost!
echo =====================================================
echo.

cd /d "%~dp0.."

echo [1/1] Running seed_demo_data.py ...
python scripts\seed_demo_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FAILED] Seed script returned error %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo.
echo [DONE] Demo data has been reset successfully.
