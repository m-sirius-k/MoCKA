@echo off
chcp 65001 >nul
cd /d C:\Users\sirok\MoCKA

echo MoCKA Starting...

REM ============================================================
REM [PHASE 1] 並列バックグラウンド処理
REM  ping_generator / UTF-8チェック / TIC / CloudFlare / git は全部並列
REM ============================================================
echo [PHASE 1] Background jobs launching...

REM ping_generator（DNA注入準備）
start /B "" python interface\ping_generator.py

REM UTF-8 mandate check（エラー時のみ警告表示・起動はブロックしない）
start /B "" cmd /c "python check_utf8_mandate.py || echo [WARN] UTF-8 check FAILED"

REM TIC: tech_watcher → risk_scorer 直列（前段依存あり）バックグラウンド
start /B "" cmd /c "python interface\tech_watcher.py && python interface\risk_scorer.py"

REM Cloudflare sync + git push バックグラウンド
start /B "" cmd /c "python PlanningCaliber\workshop\mocka-cloudflare\export_for_cloudflare.py && git add data\MOCKA_OVERVIEW.json data\MOCKA_TODO.json data\lever_essence.json data\events_latest.json >nul 2>&1 && git diff --cached --quiet || git commit -m \"data: sync %DATE% %TIME%\" && git push origin main"

REM ============================================================
REM [PHASE 2] Comet (Perplexity) 起動
REM ============================================================
taskkill /F /IM comet.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222

REM ============================================================
REM [PHASE 3] Windows Terminal タブ群 一括起動
REM  MeCab → 1秒後に全タブを一気に open
REM ============================================================
start "" wt new-tab --title "MoCKA-MECAB" --tabColor "#2d2d5f" wsl -e bash -c "python3 /home/m_kimura/mecab_service.py"
timeout /t 1 /nobreak > nul

wt -w 0 ^
  new-tab --title "MoCKA-APP"       --tabColor "#005700" cmd /k "cd /d C:\Users\sirok\MoCKA && python app.py" ^
; new-tab --title "MoCKA-MCP"       --tabColor "#5f1e3a" cmd /k "cd /d C:\Users\sirok\MoCKA && python mocka_mcp_server.py" ^
; new-tab --title "MoCKA-NGROK"     --tabColor "#3a1e5f" cmd /k "ngrok start mocka_mcp" ^
; new-tab --title "MoCKA-CALIBER"   --tabColor "#1e3a5f" cmd /k "cd /d C:\Users\sirok\MoCKA\caliber\chat_pipeline && python mocka_caliber_server.py" ^
; new-tab --title "MoCKA-RUNTIME-B" --tabColor "#5f3a00" cmd /k "cd /d C:\Users\sirok\MoCKA\runtime_b && mocka_runtime_b.exe" ^
; new-tab --title "MoCKA-SEO-OS"    --tabColor "#5f3a1e" cmd /k "cd /d C:\Users\sirok\MoCKA\PlanningCaliber\workshop\seo-os\command_center && python app.py" ^
; new-tab --title "MoCKA-WORK"                           cmd /k "cd /d C:\Users\sirok\MoCKA" ^
; new-tab --title "MoCKA-WATCHER"   --tabColor "#1e5f3a" cmd /k "cd /d C:\Users\sirok\MoCKA && set MOCKA_FIREBASE_KEY_PATH=A:\secrets\mocka-knowledge-gate.json && python interface\mocka_watcher.py" ^
; new-tab --title "HEALTH-CHECK"    --tabColor "#5f5f00" cmd /k "cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python interface/health_check.py && pause" ^
; new-tab --title "BEE-DAILY"       --tabColor "#005f5f" cmd /k "cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python structural/bee.py --daily && pause"

REM ============================================================
REM [PHASE 4] ブラウザ起動（WT起動完了まで2秒待つ）
REM ============================================================
timeout /t 2 /nobreak > nul
start "" http://localhost:5000
