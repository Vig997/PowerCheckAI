@echo off
rem PowerCheck AI - Frontend installer
rem Installs frontend dependencies using npm from the frontend folder.
rem The script works after moving the project because it resolves paths from %~dp0.

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"

cd /d "%FRONTEND%"

where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found on PATH.
  echo Install Node.js LTS from https://nodejs.org/ and reopen your terminal.
  pause
  exit /b 1
)

echo Installing frontend dependencies...
npm install

echo.
echo Frontend setup complete.
echo Next: run run_frontend.bat or runfs.bat
pause
