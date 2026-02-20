@echo off
REM ╔══════════════════════════════════════════════════════════════════╗
REM ║  P.S.AI — Windows Launcher                                      ║
REM ║  Double-click to start. Run install.bat first.                   ║
REM ║  Stop: Close this window or press Ctrl+C.                        ║
REM ╚══════════════════════════════════════════════════════════════════╝

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PORT=8000"
if defined PSAI_PORT set "PORT=%PSAI_PORT%"

echo.
echo ================================================================
echo   P.S.AI — Starting...
echo ================================================================
echo.

REM ── Check install ───────────────────────────────────────────────

if not exist "%VENV_DIR%" (
    echo   Error: Virtual environment not found.
    echo   Please run install.bat first.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo   Error: Ollama is not installed.
    echo   Please run install.bat first.
    pause
    exit /b 1
)

REM ── Start Ollama ────────────────────────────────────────────────

curl -sf http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo   OK Ollama is already running
) else (
    echo   Starting Ollama...
    start /b ollama serve >nul 2>&1
    timeout /t 5 /nobreak >nul
    echo   OK Ollama started
)

REM ── Start backend ──────────────────────────────────────────────

echo   Starting P.S.AI backend on port %PORT%...

call "%VENV_DIR%\Scripts\activate.bat"

set "PSAI_ONTOLOGY_PATH=%SCRIPT_DIR%ontology"
set "PSAI_DB_PATH=%SCRIPT_DIR%backend\data\psai.db"
set "OLLAMA_BASE_URL=http://localhost:11434"

echo.
echo ================================================================
echo   P.S.AI is running!
echo ================================================================
echo.
echo   API docs:    http://localhost:%PORT%/docs
echo   Health:      http://localhost:%PORT%/api/health
echo   Personas:    http://localhost:%PORT%/api/personas
echo.
echo   Close this window to stop the server.
echo.

REM Open browser
start "" "http://localhost:%PORT%/docs"

REM Start backend (this blocks until Ctrl+C / window close)
cd /d "%SCRIPT_DIR%backend"
uvicorn app.main:app --host 127.0.0.1 --port %PORT%
