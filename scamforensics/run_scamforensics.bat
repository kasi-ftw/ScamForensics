@echo off
setlocal
set "PROJECT_ROOT=%~dp0"

if not exist "%PROJECT_ROOT%backend\.venv\Scripts\python.exe" (
    echo Backend virtual environment was not found.
    echo Run the first-time setup commands in README.md, then run this file again.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%frontend\node_modules\.bin\vite.cmd" (
    echo Frontend dependencies were not found.
    echo Run "npm install" in the frontend folder, then run this file again.
    pause
    exit /b 1
)

start "ScamForensics Backend" cmd /k "cd /d ""%PROJECT_ROOT%backend"" && ""%PROJECT_ROOT%backend\.venv\Scripts\python.exe"" -m uvicorn app.main:app --reload --port 8000"
start "ScamForensics Frontend" cmd /k "cd /d ""%PROJECT_ROOT%frontend"" && call npm run dev"

timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"

endlocal
