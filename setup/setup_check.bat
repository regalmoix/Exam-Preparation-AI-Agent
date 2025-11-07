@echo off
REM Windows batch file wrapper for setup_check.py
REM This makes it easier to run on Windows

echo Running Setup Verification Script...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Change to the directory where this script is located
cd /d "%~dp0"

REM Run the Python script
python setup_check.py

REM Pause so user can see the output
echo.
pause

