@echo off
echo === MoCKA FULL RESTART ===

echo Stopping existing MoCKA processes...
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\sirok\MoCKA\singleton_enforce.ps1" -Pattern "ping_generator\.py|sync_watch\.py|tech_watcher\.py|risk_scorer\.py|essence_auto_updater\.py|check_utf8_mandate\.py|app\.py|mocka_mcp_server\.py|gateway\.py|living_room[\\/]hub\.py"

timeout /t 3 /nobreak >nul

REM Residual check only -- warns, does not abort. MoCKA-START.bat's own
REM pre-launch guard is the final gate if a process failed to stop.
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\sirok\MoCKA\residual_check.ps1"

echo Starting MoCKA...
call "C:\Users\sirok\MoCKA\MoCKA-START.bat"

echo === RESTART COMPLETE ===
pause
