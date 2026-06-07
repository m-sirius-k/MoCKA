@echo off
chcp 65001 >nul
title PR-OS Command Center

echo.
echo  ██████╗ ██████╗       ██████╗ ███████╗
echo  ██╔══██╗██╔══██╗     ██╔═══██╗██╔════╝
echo  ██████╔╝██████╔╝     ██║   ██║███████╗
echo  ██╔═══╝ ██╔══██╗     ██║   ██║╚════██║
echo  ██║     ██║  ██║     ╚██████╔╝███████║
echo  ╚═╝     ╚═╝  ╚═╝      ╚═════╝ ╚══════╝
echo  MoCKA Knowledge Distribution Layer
echo.

set PROS_DIR=%~dp0
cd /d "%PROS_DIR%"

echo [1/3] Command Center 起動中... (http://localhost:8740)
start "PR-OS Server" /min python -m http.server 8740 --directory command_center
timeout /t 1 /nobreak >nul

echo [2/3] TSI ヘルスチェック実行中...
python -X utf8 pros.py health

echo [3/3] ブラウザを開きます...
start http://localhost:8740

echo.
echo  PR-OS 起動完了
echo  Command Center : http://localhost:8740
echo  CLI            : python pros.py --help
echo.
echo  Daemon を起動するには別ウィンドウで:
echo    python scheduler/daemon.py
echo.
pause
