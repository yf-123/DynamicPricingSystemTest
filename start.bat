@echo off
echo Starting Dynamic Pricing System...
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo Virtual environment not found. Running setup...
    python setup.py
    echo.
)

REM Start backend in a new window
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python app.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul 