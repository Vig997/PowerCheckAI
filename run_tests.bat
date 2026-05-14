@echo off
rem PowerCheck AI - Test runner
rem Runs backend pytest, then runs the frontend production build if npm dependencies exist.
rem Use this before demos to catch API and UI compile issues.

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

cd /d "%BACKEND%"
echo Running backend tests...
"%PYTHON%" -m pytest
if errorlevel 1 (
  echo Backend tests failed.
  pause
  exit /b 1
)

cd /d "%FRONTEND%"
if not exist "node_modules" (
  echo Frontend dependencies were not found. Skipping frontend build.
  echo Run install_frontend.bat to enable frontend checks.
  pause
  exit /b 0
)

if exist "node_modules\.bin\tsc.cmd" if exist "node_modules\.bin\vite.cmd" (
  echo Running frontend type check...
  call "node_modules\.bin\tsc.cmd" --noEmit
  if errorlevel 1 (
    echo Frontend type check failed.
    pause
    exit /b 1
  )

  echo Running frontend build...
  call "node_modules\.bin\vite.cmd" build --config vite.config.ts
  if errorlevel 1 (
    echo Frontend build failed.
    pause
    exit /b 1
  )
) else (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo npm was not found and local frontend binaries were not available.
    echo Run install_frontend.bat after installing Node.js LTS.
    pause
    exit /b 1
  )

  echo Running frontend build...
  npm run build
  if errorlevel 1 (
    echo Frontend build failed.
    pause
    exit /b 1
  )
)

echo.
echo All checks passed.
pause
