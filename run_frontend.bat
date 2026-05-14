@echo off
rem PowerCheck AI - Frontend runner
rem This script works from any folder because %~dp0 points to the project root.
rem It starts the Vite dev server. Vite proxies /api to the backend on port 8000.

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"

cd /d "%FRONTEND%"

if not exist "node_modules" (
  echo Frontend dependencies were not found.
  echo Run install_frontend.bat first.
  pause
  exit /b 1
)

echo Starting PowerCheck AI frontend at http://127.0.0.1:5173
if exist "node_modules\.bin\vite.cmd" (
  call "node_modules\.bin\vite.cmd" --host 127.0.0.1 --port 5173
) else (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo npm was not found and local Vite was not available.
    echo Run install_frontend.bat after installing Node.js LTS.
    pause
    exit /b 1
  )
  npm run dev
)
