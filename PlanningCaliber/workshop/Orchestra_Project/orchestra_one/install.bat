@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================================
echo  Orchestra One - Installer
echo  Playwright自律実行ホストをセットアップします
echo ============================================================
echo.

:: ── Step 1: Python確認 ──────────────────────────────────────────────────────
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pythonが見つかりません。
    echo         https://www.python.org/downloads/ からインストールしてください。
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i

:: ── Step 2: インストール先ディレクトリ ─────────────────────────────────────
set "INSTALL_DIR=%USERPROFILE%\orchestra_one"
echo.
echo インストール先: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: ── Step 3: ファイルをコピー ────────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
copy /Y "%SCRIPT_DIR%orchestra_one_host.py" "%INSTALL_DIR%\" > nul
copy /Y "%SCRIPT_DIR%run_host.bat"           "%INSTALL_DIR%\" > nul
copy /Y "%SCRIPT_DIR%requirements.txt"       "%INSTALL_DIR%\" > nul
echo [OK] ファイルをコピーしました

:: ── Step 4: Playwright インストール ────────────────────────────────────────
echo.
echo [Step 4] Playwright をインストール中...
python -m pip install --upgrade pip --quiet
python -m pip install playwright --quiet
if errorlevel 1 (
    echo [ERROR] pip install playwright に失敗しました
    pause
    exit /b 1
)
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] playwright install chromium に失敗しました
    pause
    exit /b 1
)
echo [OK] Playwright インストール完了

:: ── Step 5: 拡張機能IDの入力 ────────────────────────────────────────────────
echo.
echo ============================================================
echo  [Step 5] Chrome拡張機能IDの入力
echo ============================================================
echo  chrome://extensions を開き、Orchestra の拡張機能IDをコピーしてください。
echo  例: abcdefghijklmnopqrstuvwxyz123456
echo.
set /p EXT_ID="拡張機能IDを入力してください: "
if "%EXT_ID%"=="" (
    echo [WARNING] IDが空です。後でNMホスト設定ファイルを手動で編集してください。
    set "EXT_ID=REPLACE_WITH_EXTENSION_ID"
)

:: ── Step 6: NativeMessaging マニフェスト作成 ────────────────────────────────
set "NM_MANIFEST=%INSTALL_DIR%\com.sirius_lab.orchestra_one.json"
set "HOST_PATH=%INSTALL_DIR%\run_host.bat"
:: バックスラッシュをエスケープ
set "HOST_PATH_ESC=!HOST_PATH:\=\\!"

(
echo {
echo   "name": "com.sirius_lab.orchestra_one",
echo   "description": "Orchestra One - Playwright autonomous host",
echo   "path": "!HOST_PATH_ESC!",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://!EXT_ID!/"
echo   ]
echo }
) > "%NM_MANIFEST%"
echo [OK] NMホストマニフェストを作成しました: %NM_MANIFEST%

:: ── Step 7: Windowsレジストリ登録 ──────────────────────────────────────────
set "REG_KEY=HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.sirius_lab.orchestra_one"
set "NM_MANIFEST_ESC=!NM_MANIFEST:\=\\!"
reg add "%REG_KEY%" /ve /t REG_SZ /d "%NM_MANIFEST%" /f > nul
if errorlevel 1 (
    echo [ERROR] レジストリ登録に失敗しました
    pause
    exit /b 1
)
echo [OK] Chromeレジストリに登録しました

:: ── Vivaldi / Edge / Brave 対応 (オプション) ────────────────────────────────
reg query "HKCU\SOFTWARE\Vivaldi" > nul 2>&1
if not errorlevel 1 (
    reg add "HKCU\SOFTWARE\Vivaldi\NativeMessagingHosts\com.sirius_lab.orchestra_one" /ve /t REG_SZ /d "%NM_MANIFEST%" /f > nul
    echo [OK] Vivaldi にも登録しました
)

:: ── 完了 ────────────────────────────────────────────────────────────────────
echo.
echo ============================================================
echo  Orchestra One インストール完了！
echo ============================================================
echo.
echo 次のステップ:
echo   1. Chromeを再起動してください
echo   2. Orchestra拡張機能のSettingsでOneライセンスキーを入力
echo   3. claude.ai で回答を受け取ったら ⚡ Orchestra One ボタンをクリック
echo.
pause
