@echo off
chcp 65001 > nul
echo vasAI COMMAND CENTER - Starting...

start "vasAI API" cmd /k "cd /d C:\Users\sirok\MoCKA\PlanningCaliber\workshop\vasAI_Project && python api/app.py"

timeout /t 3 > nul

start "" "C:\Users\sirok\MoCKA\PlanningCaliber\workshop\vasAI_Project\dashboard\index.html"

echo vasAI Running on port 6000
