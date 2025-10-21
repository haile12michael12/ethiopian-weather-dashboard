@echo off
echo Starting Ethiopian Weather Dashboard...

echo Starting backend server...
cd backend
start "Backend Server" python api.py

timeout /t 5

echo Starting frontend server...
cd ../frontend
npm run dev

echo Press any key to stop servers...
pause >nul
taskkill /f /im python.exe