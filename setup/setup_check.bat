@echo off
REM Windows batch file wrapper for setup_check.py
REM This makes it easier to run on Windows
REM Enhanced with winget detection and better error handling

echo Running Setup Verification Script...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Attempting to check for winget to auto-install Python...
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo winget found. You can install Python with:
        echo   winget install Python.Python.3.11
        echo.
    ) else (
        echo winget not available. Please install Python 3.11+ manually:
        echo   Download from: https://www.python.org/downloads/
        echo.
    )
    pause
    exit /b 1
)

REM Check for winget availability (for auto-installation)
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo winget detected - auto-installation will be attempted for missing dependencies
) else (
    echo Note: winget not found. Some dependencies may need manual installation.
    echo Install winget from Microsoft Store for automatic dependency installation.
)
echo.

REM Change to the directory where this script is located
cd /d "%~dp0"

REM Run the Python script
python setup_check.py

REM Capture exit code
set EXIT_CODE=%errorlevel%

REM Pause so user can see the output
echo.
if %EXIT_CODE% neq 0 (
    echo.
    echo Setup check completed with errors. Please review the output above.
) else (
    echo.
    echo Setup check completed successfully!
)
pause

exit /b %EXIT_CODE%

