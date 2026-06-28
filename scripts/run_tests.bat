@echo off
REM run_tests.bat
REM Phase 2 — Run all integration tests in one step.
REM
REM Usage:
REM     scripts\run_tests.bat
REM

cd /d "%~dp0.."

echo =====================================================
echo   Running integration tests (pytest)
echo =====================================================

pytest tests\integration -q %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All integration tests passed.
) else (
    echo.
    echo Some tests FAILED — see output above.
    exit /b %ERRORLEVEL%
)
