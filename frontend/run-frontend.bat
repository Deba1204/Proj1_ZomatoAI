@echo off
REM Add Node.js to PATH for this session (default LTS install location)
set "NODE_PATH=C:\Program Files\nodejs"
set "PATH=%NODE_PATH%;%PATH%"

REM If Node is in a different location, set NODE_PATH above or install to default.

echo Checking Node and npm...
where node >nul 2>&1 || (echo Node not found. Install from https://nodejs.org/ and run this again. & pause & exit /b 1)
where npm >nul 2>&1 || (echo npm not found. Add "C:\Program Files\nodejs" to your system PATH. & pause & exit /b 1)

cd /d "%~dp0"
echo Installing dependencies...
call npm install
if errorlevel 1 (echo npm install failed. & pause & exit /b 1)
echo.
echo Starting frontend dev server...
echo Open http://localhost:5173 in your browser.
echo Press Ctrl+C to stop.
call npm run dev
pause
