# Create Windows Task Scheduler task for automated trading
$action = New-ScheduledTaskAction -Execute "C:\trading_bot_starter_full\auto_trade.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken

Register-ScheduledTask -TaskName "Trading Bot Daily" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated Trading Bot - Runs daily at 9 AM"

Write-Host "✅ Scheduled task created: 'Trading Bot Daily'"
Write-Host "📅 Runs daily at 9:00 AM"
Write-Host "🔧 To modify: Open Task Scheduler and find 'Trading Bot Daily'"
