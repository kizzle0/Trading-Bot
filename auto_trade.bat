@echo off
echo Starting Automated Trading Bot...
echo %date% %time% - Trading session started >> trading_log.txt

cd /d "%~dp0"

REM Check if dashboard is already running
netstat -an | find "8501" > nul
if %errorlevel% == 0 (
    echo Dashboard already running, skipping startup
    goto :start_trading
)

REM Start dashboard in background
echo Starting dashboard...
start /B .venv\Scripts\python.exe -m streamlit run dashboard.py --server.headless true --server.port 8501

REM Wait for dashboard to start
timeout /t 10 /nobreak > nul

:start_trading
echo Starting automated trading...
.venv\Scripts\python.exe run_live.py --auto-trade

echo %date% %time% - Trading session ended >> trading_log.txt
