@echo off
echo Starting Universal Trading Bot Dashboard...
echo.
echo The dashboard will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the dashboard
echo.
cd /d "%~dp0"

REM Use virtual environment Python where all packages are installed
echo Using virtual environment Python (where all packages are installed)...
.venv\Scripts\python.exe -m streamlit run dashboard.py

pause
