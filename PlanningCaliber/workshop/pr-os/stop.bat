@echo off
chcp 65001 >nul
echo PR-OS サーバーを停止します...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8740"') do (
    taskkill /PID %%a /F >nul 2>&1
    echo Port 8740 解放: PID %%a
)
echo 完了.
pause
