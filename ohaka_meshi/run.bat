@echo off
setlocal
cd /d "%~dp0"

if exist venv goto activate

echo Setting up for the first time, please wait...
python -m venv venv
if errorlevel 1 goto nopython
call venv\Scripts\activate.bat
pip install -r requirements.txt
goto run

:activate
call venv\Scripts\activate.bat
goto run

:nopython
echo Python was not found. Please install Python 3.11+ from python.org
echo (Check "Add python.exe to PATH" during installation.)
pause
exit /b 1

:run
start "" /min cmd /c "timeout /t 2 >nul && start http://127.0.0.1:5000"
python app.py

echo.
echo Server stopped.
pause
