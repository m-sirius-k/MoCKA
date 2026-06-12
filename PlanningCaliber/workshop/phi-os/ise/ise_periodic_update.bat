@echo off
REM ISE Institution State 定期更新（5分間隔）
REM MoCKA-START.bat から start /B で起動される常駐ループ

:loop
cd /d C:\Users\sirok\MoCKA
python PlanningCaliber\workshop\phi-os\ise\update_state.py
timeout /t 300 /nobreak > nul
goto loop
