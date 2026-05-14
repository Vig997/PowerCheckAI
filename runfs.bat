@echo off
rem PowerCheck AI - one-command full-stack runner
rem Run this from VS Code's integrated terminal with: .\runfs
rem The backend starts in the same terminal session using start /b, then the frontend runs in the foreground.

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "PYTHON=%BACKEND%\.venv\Scripts\python.exe"

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

if not exist "%FRONTEND%\node_modules" (
  echo Frontend dependencies were not found.
  echo Run install_frontend.bat first.
  pause
  exit /b 1
)

echo Starting PowerCheck AI backend at http://127.0.0.1:8000
start "PowerCheck Backend" /b cmd /d /c "cd /d ""%BACKEND%"" && ""%PYTHON%"" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting PowerCheck AI frontend at http://127.0.0.1:5173
cd /d "%FRONTEND%"
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
