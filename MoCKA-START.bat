@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d C:\Users\sirok\MoCKA

echo MoCKA Starting...

REM ============================================================
REM [PHASE 1] Background jobs
REM ============================================================
echo [PHASE 1] Background jobs launching...

start /B "" python interface\ping_generator.py
start /B "" cmd /c "python check_utf8_mandate.py || echo [WARN] UTF-8 check FAILED"
start /B "" cmd /c "python interface\tech_watcher.py && python interface\risk_scorer.py"
start /B "" cmd /c "cd /d C:\Users\sirok\MoCKA && PlanningCaliber\workshop\phi-os\ise\ise_periodic_update.bat"
start /B "" cmd /c "python PlanningCaliber\workshop\mocka-cloudflare\sync_watch.py"
start /B "" cmd /k "cd /d C:\Users\sirok\MoCKA && set PYTHONUTF8=1 && python interface\essence_auto_updater.py"

REM ============================================================
REM [PHASE 2] Comet
REM ============================================================
taskkill /F /IM comet.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222

REM ============================================================
REM [PHASE 3] Windows Terminal tabs
REM ============================================================
start "" wt new-tab --title "MoCKA-MECAB" --tabColor "#2d2d5f" wsl -e bash -c "python3 /home/m_kimura/mecab_service.py"
timeout /t 1 /nobreak > nul

wt -w 0 ^
  new-tab --title "MoCKA-APP"       --tabColor "#005700" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && python app.py" ^
; new-tab --title "MoCKA-MCP"       --tabColor "#5f1e3a" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && python mocka_mcp_server.py" ^
; new-tab --title "MoCKA-NGROK"     --tabColor "#3a1e5f" cmd /k "ngrok start mocka_mcp" ^
; new-tab --title "MoCKA-CALIBER"   --tabColor "#1e3a5f" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA\caliber\chat_pipeline && python mocka_caliber_server.py" ^
; new-tab --title "MoCKA-CONNECTOR" --tabColor "#3a5f1e" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA\gateway && python gateway.py" ^
; new-tab --title "MoCKA-RUNTIME-B" --tabColor "#5f3a00" cmd /k "cd /d C:\Users\sirok\MoCKA\runtime_b && mocka_runtime_b.exe" ^
; new-tab --title "MoCKA-SEO-OS"    --tabColor "#5f3a1e" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA\PlanningCaliber\workshop\seo-os\command_center && python app.py" ^
; new-tab --title "MoCKA-WORK"                           cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA" ^
; new-tab --title "MoCKA-WATCHER"   --tabColor "#1e5f3a" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && set MOCKA_FIREBASE_KEY_PATH=A:\secrets\mocka-knowledge-gate.json && python interface\mocka_watcher.py" ^
; new-tab --title "HEALTH-CHECK"    --tabColor "#5f5f00" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python interface/health_check.py && pause" ^
; new-tab --title "BEE-DAILY"       --tabColor "#005f5f" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python structural/bee.py --daily && pause" ^
; new-tab --title "LIVING-ROOM"     --tabColor "#3a1e5f" cmd /k "set PYTHONUTF8=1 && cd /d C:\Users\sirok\MoCKA && python living_room/hub.py"

REM ============================================================
REM [PHASE 4] Browser
REM ============================================================
timeout /t 2 /nobreak > nul
start "" http://localhost:5000

REM ============================================================
REM [PHASE 5] TIC Risk Dashboard
REM ============================================================
start /B "" cmd /c "cd /d C:\Users\sirok\MoCKA && python interface\risk_interpreter.py"