#!/usr/bin/env python3
"""
Setup automated trading with Windows Task Scheduler
"""
import os
import subprocess
import sys

def create_auto_trade_script():
    """Create a script that runs automated trading"""
    script_content = '''@echo off
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
start /B .venv\\Scripts\\python.exe -m streamlit run dashboard.py --server.headless true --server.port 8501

REM Wait for dashboard to start
timeout /t 10 /nobreak > nul

:start_trading
echo Starting automated trading...
.venv\\Scripts\\python.exe run_live.py --auto-trade

echo %date% %time% - Trading session ended >> trading_log.txt
'''
    
    with open('auto_trade.bat', 'w') as f:
        f.write(script_content)
    
    print("✅ Created auto_trade.bat script")

def create_task_scheduler_script():
    """Create PowerShell script to setup Windows Task Scheduler"""
    ps_script = '''# Create Windows Task Scheduler task for automated trading
$action = New-ScheduledTaskAction -Execute "C:\\trading_bot_starter_full\\auto_trade.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken

Register-ScheduledTask -TaskName "Trading Bot Daily" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated Trading Bot - Runs daily at 9 AM"

Write-Host "✅ Scheduled task created: 'Trading Bot Daily'"
Write-Host "📅 Runs daily at 9:00 AM"
Write-Host "🔧 To modify: Open Task Scheduler and find 'Trading Bot Daily'"
'''
    
    with open('setup_scheduler.ps1', 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print("✅ Created setup_scheduler.ps1 script")

def main():
    print("🤖 Automated Trading Setup")
    print("=" * 40)
    
    print("This will set up automated trading for your bot.")
    print()
    
    # Create automation scripts
    create_auto_trade_script()
    create_task_scheduler_script()
    
    print("\n📋 Setup Options:")
    print()
    print("🕐 Option 1: Windows Task Scheduler (Local)")
    print("• Run: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1")
    print("• Bot runs automatically every day at 9 AM")
    print("• Your computer must be on")
    print()
    print("🌐 Option 2: Cloud Deployment (Recommended)")
    print("• Run: python deploy_to_cloud.py")
    print("• Access from anywhere 24/7")
    print("• No need to keep computer on")
    print()
    print("📱 Option 3: Manual Control")
    print("• Use the dashboard from your phone")
    print("• Start/stop trading anytime")
    print("• Monitor from anywhere")
    print()
    
    print("💰 Recommended Setup:")
    print("1. Deploy to cloud for 24/7 access")
    print("2. Set up $50-100 in each broker account")
    print("3. Configure risk settings (1-2% per trade)")
    print("4. Monitor daily via web dashboard")

if __name__ == "__main__":
    main()
