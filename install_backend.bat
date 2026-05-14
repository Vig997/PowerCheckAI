@echo off
rem PowerCheck AI - Backend installer
rem Creates backend\.venv and installs Python dependencies from backend\requirements.txt.
rem This uses cmd/batch commands, not PowerShell, to avoid execution-policy issues.

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "VENV=%BACKEND%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PYTHON_CREATE_CMD="

cd /d "%BACKEND%"

python --version >nul 2>nul
if not errorlevel 1 set "PYTHON_CREATE_CMD=python"

if "%PYTHON_CREATE_CMD%"=="" (
  py --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CREATE_CMD=py -3"
)

if exist "%PYTHON%" (
  "%PYTHON%" --version >nul 2>nul
  if errorlevel 1 (
    echo Existing backend virtual environment is broken.
    echo Removing backend\.venv so it can be recreated.
    rmdir /s /q "%VENV%"
  )
)

if not exist "%PYTHON%" (
  if "%PYTHON_CREATE_CMD%"=="" (
    echo Python was not found on PATH.
    echo Install Python 3.12+ from https://www.python.org/downloads/ and reopen your terminal.
    pause
    exit /b 1
  )

  echo Creating backend virtual environment...
  %PYTHON_CREATE_CMD% -m venv .venv
  if errorlevel 1 (
    echo Could not create .venv.
    echo Make sure Python 3.12+ is installed correctly.
    pause
    exit /b 1
  )
)

echo Installing backend dependencies...
"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r requirements.txt

echo.
echo Backend setup complete.
echo Next: run run_backend.bat or runfs.bat
pause
