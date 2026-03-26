@echo off
echo === MoCKA FULL RESTART ===

echo Killing Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo Killing extra PowerShell...
taskkill /F /IM powershell.exe >nul 2>&1

timeout /t 2 >nul

echo Restarting main loop...
cd /d C:\Users\sirok\MoCKA\runtime
start cmd /k python main_loop.py

echo Restarting intent ingestor (manual trigger ready)...
start cmd /k echo READY FOR intent_ingestor

echo === RESTART COMPLETE ===
pause
