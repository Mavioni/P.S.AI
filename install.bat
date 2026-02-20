@echo off
REM ╔══════════════════════════════════════════════════════════════════╗
REM ║  P.S.AI — Windows Installer                                     ║
REM ║  Double-click this file after extracting the zip.                ║
REM ╚══════════════════════════════════════════════════════════════════╝

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "MODEL=llama3"
if defined PSAI_MODEL set "MODEL=%PSAI_MODEL%"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo.
echo ================================================================
echo   P.S.AI — Posthumous Social Artificial Intelligence
echo   Windows Installer
echo ================================================================
echo.

REM ── Step 1: Check Python ────────────────────────────────────────

echo [1/5] Checking Python...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   X Python is not installed.
    echo.
    echo     Please download and install Python 3.11+ from:
    echo     https://www.python.org/downloads/
    echo.
    echo     IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_VERSION=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.version_info.major)"') do set PY_MAJOR=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.version_info.minor)"') do set PY_MINOR=%%i

if %PY_MAJOR% lss 3 (
    echo   X Python %PY_VERSION% found, but P.S.AI requires Python 3.11+.
    pause
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 11 (
    echo   X Python %PY_VERSION% found, but P.S.AI requires Python 3.11+.
    pause
    exit /b 1
)

echo   OK Python %PY_VERSION%

REM ── Step 2: Create virtual environment ──────────────────────────

echo.
echo [2/5] Setting up Python backend...

if not exist "%VENV_DIR%" (
    echo   Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

echo   Installing backend dependencies (this may take a minute)...
pip install --quiet --upgrade pip
pip install --quiet "%SCRIPT_DIR%backend[security]"

echo   OK Backend installed

REM ── Step 3: Check Ollama ────────────────────────────────────────

echo.
echo [3/5] Checking Ollama (local AI engine)...

where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo   OK Ollama is already installed
    goto :pull_model
)

echo   Ollama is not installed.
echo.
echo   Please download and install Ollama from:
echo   https://ollama.com/download/windows
echo.
echo   After installing Ollama, run this installer again.
echo.
pause
exit /b 1

REM ── Step 4: Pull model ─────────────────────────────────────────

:pull_model
echo.
echo [4/5] Downloading AI model (%MODEL%)...
echo   This downloads ~4 GB on first run. Please be patient.

REM Start Ollama if not running
curl -sf http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo   Starting Ollama server...
    start /b ollama serve >nul 2>&1
    timeout /t 5 /nobreak >nul
)

ollama pull %MODEL%
echo   OK Model '%MODEL%' is ready

REM ── Step 5: Prepare data directory ─────────────────────────────

echo.
echo [5/5] Preparing data directory...
if not exist "%SCRIPT_DIR%backend\data" mkdir "%SCRIPT_DIR%backend\data"
echo   OK Data directory ready

REM ── Done ────────────────────────────────────────────────────────

echo.
echo ================================================================
echo   Installation complete!
echo ================================================================
echo.
echo   To start P.S.AI, double-click:
echo.
echo     launch.bat
echo.
echo   Then open http://localhost:8000/docs in your browser.
echo.
pause
