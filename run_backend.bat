@echo off
rem PowerCheck AI - Backend runner
rem This script works from any folder because %~dp0 points to the project root.
rem It avoids PowerShell execution-policy issues by using activate.bat and python.exe directly.

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "VENV=%BACKEND%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"

cd /d "%BACKEND%"

if not exist "%PYTHON%" (
  echo Backend virtual environment was not found.
  echo Run install_backend.bat first.
  pause
  exit /b 1
)

"%PYTHON%" --version >nul 2>nul
if errorlevel 1 (
  echo Backend virtual environment exists, but its Python launcher is broken.
  echo Run install_backend.bat again to recreate backend\.venv.
  pause
  exit /b 1
)

call "%VENV%\Scripts\activate.bat"
echo Starting PowerCheck AI backend at http://127.0.0.1:8000
"%PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
