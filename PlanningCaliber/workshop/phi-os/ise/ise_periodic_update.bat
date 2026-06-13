@echo off
REM ISE Institution State periodic update
REM Called from MoCKA-START.bat via start /B
:loop
cd /d C:\Users\sirok\MoCKA
python PlanningCaliber\workshop\phi-os\ise\update_state.py
timeout /t 300 /nobreak > nul
goto loop