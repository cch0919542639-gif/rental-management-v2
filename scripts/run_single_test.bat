@echo off
REM run_single_test.bat — Run one integration test file with verbose output.
REM Usage: scripts\run_single_test.bat <filename>
REM Example: scripts\run_single_test.bat test_maintenance_readiness.py

setlocal
set "SCRIPT=%~1"

if "%SCRIPT%"=="" (
    echo Usage: run_single_test.bat ^<test_filename^>
    echo.
    echo Example: run_single_test.bat test_maintenance_readiness.py
    echo.
    echo Available tests:
    echo ----------------------------------------
    dir /b "%~dp0..\tests\integration\*.py" 2>nul
    exit /b 1
)

set "TEST_PATH=%~dp0..\tests\integration\%SCRIPT%"

if not exist "%TEST_PATH%" (
    echo ERROR: File not found: %TEST_PATH%
    exit /b 1
)

cd /d "%~dp0.."
echo =============================================
echo   Running: %SCRIPT%
echo =============================================
pytest "%TEST_PATH%" -v --tb=short

if %ERRORLEVEL% EQU 0 (
    echo.
    echo PASSED: %SCRIPT%
) else (
    echo.
    echo FAILED: %SCRIPT%
)
