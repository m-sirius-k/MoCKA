@echo off
chcp 65001 > nul
title NTP API Server
echo ========================================
echo  NTP 保険プランニングツール - APIサーバー
echo ========================================
echo.

cd /d "%~dp0"

:: 依存パッケージ確認
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [依存パッケージをインストールしています...]
    pip install -r requirements.txt
    echo.
)

echo [サーバー起動中...]
echo  URL: http://localhost:8400
echo  API仕様: http://localhost:8400/docs
echo.
echo  停止するには Ctrl+C を押してください
echo.

python -m uvicorn src.api.main:app --reload --port 8400 --host 0.0.0.0

pause
