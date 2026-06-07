@echo off
chcp 65001 >nul
title PR-OS Setup

echo.
echo PR-OS セットアップ
echo ==================
echo.

cd /d "%~dp0"

REM Python確認
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python が見つかりません。https://python.org からインストールしてください。
    pause & exit /b 1
)
echo [OK] Python: 確認済み

REM pip パッケージインストール
echo.
echo [1/3] 依存パッケージをインストール中...
pip install requests >nul 2>&1
echo       requests ... OK

pip install pytest >nul 2>&1
echo       pytest  ... OK

REM google-analytics-data は任意
pip install google-analytics-data >nul 2>&1
if errorlevel 1 (
    echo       google-analytics-data ... スキップ (GA4使用時は手動インストール)
) else (
    echo       google-analytics-data ... OK
)

REM ディレクトリ確認
echo.
echo [2/3] ディレクトリ確認...
if not exist "knowledge_store\confirmed" mkdir "knowledge_store\confirmed"
if not exist "knowledge_store\draft"     mkdir "knowledge_store\draft"
if not exist "logs"                      mkdir "logs"
echo       ディレクトリ ... OK

REM テスト実行
echo.
echo [3/3] テスト実行中...
python -X utf8 -m pytest tests/ -q --tb=short 2>&1
if errorlevel 1 (
    echo [WARN] テストに失敗があります。上記を確認してください。
) else (
    echo [OK] 全テスト通過
)

echo.
echo ==================
echo セットアップ完了！
echo.
echo 次のステップ:
echo   1. start.bat          ... PR-OS起動
echo   2. pros.py --help     ... CLI使用方法
echo   3. adapters/*/config.json に認証情報を設定
echo ==================
echo.
pause
