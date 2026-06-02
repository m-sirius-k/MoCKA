@echo off
python C:\Users\sirok\MoCKA\interface\ping_generator.py
timeout /t 2 /nobreak > nul
echo MoCKA Starting...
echo [UTF-8 MANDATE CHECK]
python C:\Users\sirok\MoCKA\check_utf8_mandate.py
if %ERRORLEVEL% NEQ 0 (
    echo UTF-8�ᔽ���o�I�N�����~���܂��B
    pause
    exit /b 1
)
echo UTF-8 OK

echo [TIC] Running Tech Watcher...
python C:\Users\sirok\MoCKA\interface\tech_watcher.py
echo [TIC] Updating Risk Scores...
python C:\Users\sirok\MoCKA\interface\risk_scorer.py

echo [CLOUDFLARE SYNC] Exporting data and pushing to GitHub...
python C:\Users\sirok\MoCKA\PlanningCaliber\workshop\mocka-cloudflare\export_for_cloudflare.py
cd /d C:\Users\sirok\MoCKA
git add data\MOCKA_OVERVIEW.json data\MOCKA_TODO.json data\lever_essence.json data\events_latest.json >nul 2>&1
git diff --cached --quiet
if %ERRORLEVEL% NEQ 0 (
    git commit -m "data: sync %DATE% %TIME%"
    git push origin main
    echo [SYNC] pushed to GitHub
) else (
    echo [SYNC] no changes, skip push
)

taskkill /F /IM comet.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222
timeout /t 3 /nobreak > nul
start "" wt new-tab --title "MoCKA-MECAB" --tabColor "#2d2d5f" wsl -e bash -c "python3 /home/m_kimura/mecab_service.py"
timeout /t 3 /nobreak > nul
wt -w 0 new-tab --title "MoCKA-APP" --tabColor "#005700" cmd /k "cd /d C:\Users\sirok\MoCKA && python app.py" ; new-tab --title "MoCKA-MCP" --tabColor "#5f1e3a" cmd /k "cd /d C:\Users\sirok\MoCKA && python mocka_mcp_server.py" ; new-tab --title "MoCKA-NGROK" --tabColor "#3a1e5f" cmd /k "ngrok start mocka_mcp" ; new-tab --title "MoCKA-CALIBER" --tabColor "#1e3a5f" cmd /k "cd /d C:\Users\sirok\MoCKA\caliber\chat_pipeline && python mocka_caliber_server.py" ; new-tab --title "MoCKA-RUNTIME-B" --tabColor "#5f3a00" cmd /k "cd /d C:\Users\sirok\MoCKA\runtime_b && mocka_runtime_b.exe" ; new-tab --title "MoCKA-WORK" cmd /k "cd /d C:\Users\sirok\MoCKA" ; new-tab --title "MoCKA-WATCHER" --tabColor "#1e5f3a" cmd /k "cd /d C:\Users\sirok\MoCKA && set MOCKA_FIREBASE_KEY_PATH=A:\secrets\mocka-knowledge-gate.json&& python interface\mocka_watcher.py"
timeout /t 4 /nobreak > nul
start "" http://localhost:5000

REM health_check（毎朝キャリブレーション・別ウィンドウで結果目視）
start "HEALTH" cmd /k "cd /d C:\Users\sirok\MoCKA && python interface/health_check.py && pause"

REM β Ecology 毎朝スキャン
start "BEE" cmd /k "cd /d C:\Users\sirok\MoCKA && python structural/bee.py --daily && pause"