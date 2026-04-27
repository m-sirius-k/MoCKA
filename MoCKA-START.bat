@echo off
python C:\Users\sirok\MoCKA\interface\ping_generator.py
timeout /t 2 /nobreak > nul
echo [MoCKA] Starting...
taskkill /F /IM comet.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222
timeout /t 3 /nobreak > nul
:: MeCabサービス起動（WSL2 port:5003）
start "" wt new-tab --title "MoCKA-MECAB" --tabColor "#2d2d5f" wsl -e bash -c "python3 /home/m_kimura/mecab_service.py"
timeout /t 3 /nobreak > nul
:: Windows Terminal ? 全サーバーを一括起動
wt -w 0 new-tab --title "MoCKA-APP" --tabColor "#005700" cmd /k "cd /d C:\Users\sirok\MoCKA && python app.py" ; new-tab --title "MoCKA-MCP" --tabColor "#5f1e3a" cmd /k "cd /d C:\Users\sirok\MoCKA && python mocka_mcp_server.py" ; new-tab --title "MoCKA-NGROK" --tabColor "#3a1e5f" cmd /k "ngrok start mocka_mcp" ; new-tab --title "MoCKA-CALIBER" --tabColor "#1e3a5f" cmd /k "cd /d C:\Users\sirok\MoCKA\caliber\chat_pipeline && python mocka_caliber_server.py" ; new-tab --title "MoCKA-WORK" cmd /k "cd /d C:\Users\sirok\MoCKA" ; new-tab --title "MoCKA-WATCHER" --tabColor "#1e5f3a" cmd /k "cd /d C:\Users\sirok\MoCKA && set MOCKA_FIREBASE_KEY_PATH=X:\down\mocka-knowledge-gate-firebase-adminsdk-fbsvc-53613922c1.json && python interface\mocka_watcher.py"
timeout /t 4 /nobreak > nul
start "" http://localhost:5000