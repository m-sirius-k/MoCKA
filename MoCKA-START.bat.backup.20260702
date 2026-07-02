@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d C:\Users\sirok\MoCKA

echo MoCKA Starting...

REM ============================================================
REM [PHASE 0] Cleanup stale background jobs from previous run
REM ============================================================
echo [PHASE 0] Cleaning up stale background processes...
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'ping_generator\.py|sync_watch\.py|tech_watcher\.py|risk_scorer\.py|essence_auto_updater\.py|check_utf8_mandate\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
timeout /t 1 /nobreak > nul

REM ============================================================
REM [PHASE 0.6] Pre-launch port audit (Phase5-2.2 TODO: prevent
REM stale process / new process co-listening on same port via
REM Windows SO_REUSEADDR, which silently routes requests to old
REM unpatched code after a restart)
REM ============================================================
echo [PHASE 0.6] Auditing ports 5000/5002/5679 for stale listeners...
for %%P in (5000 5002 5679) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    echo [PHASE 0.6] Stopping stale process on port %%P PID=%%a
    taskkill /F /PID %%a >nul 2>&1
  )
)
timeout /t 1 /nobreak > nul

REM ============================================================
REM [PHASE 1] Background jobs
REM ============================================================
echo [PHASE 1] Background jobs launching...

start /B "" python -X utf8 interface\ping_generator.py
start /B "" cmd /c "python -X utf8 check_utf8_mandate.py || echo [WARN] UTF-8 check FAILED"
start /B "" cmd /c "python -X utf8 interface\tech_watcher.py && python -X utf8 interface\risk_scorer.py"
start /B "" cmd /c "cd /d C:\Users\sirok\MoCKA && PlanningCaliber\workshop\phi-os\ise\ise_periodic_update.bat"
start /B "" cmd /c "python -X utf8 PlanningCaliber\workshop\mocka-cloudflare\sync_watch.py"
start /B "" cmd /k "cd /d C:\Users\sirok\MoCKA && python -X utf8 interface\essence_auto_updater.py"

REM ============================================================
REM [PHASE 2] Comet
REM ============================================================
taskkill /F /IM comet.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222

REM ============================================================
REM [PHASE 3] Windows Terminal tabs
REM ============================================================
start "" wt new-tab --title "MoCKA-MECAB" --tabColor "#2d2d5f" wsl -e bash -c "python3 -X utf8 /home/m_kimura/mecab_service.py"
timeout /t 1 /nobreak > nul

wt -w 0 ^
  new-tab --title "MoCKA-APP"       --tabColor "#005700" cmd /k "cd /d C:\Users\sirok\MoCKA && python -X utf8 app.py" ^
; new-tab --title "MoCKA-MCP"       --tabColor "#5f1e3a" cmd /k "cd /d C:\Users\sirok\MoCKA && python -X utf8 mocka_mcp_server.py" ^
; new-tab --title "MoCKA-NGROK"     --tabColor "#3a1e5f" cmd /k "ngrok start mocka_mcp" ^
; new-tab --title "MoCKA-CALIBER"   --tabColor "#1e3a5f" cmd /k "cd /d C:\Users\sirok\MoCKA\caliber\chat_pipeline && python -X utf8 mocka_caliber_server.py" ^
; new-tab --title "MoCKA-CONNECTOR" --tabColor "#3a5f1e" cmd /k "cd /d C:\Users\sirok\MoCKA\gateway && python -X utf8 gateway.py" ^
; new-tab --title "MoCKA-RUNTIME-B" --tabColor "#5f3a00" cmd /k "cd /d C:\Users\sirok\MoCKA\runtime_b && mocka_runtime_b.exe" ^
; new-tab --title "MoCKA-SEO-OS"    --tabColor "#5f3a1e" cmd /k "cd /d C:\Users\sirok\MoCKA\PlanningCaliber\workshop\seo-os\command_center && python -X utf8 app.py" ^
; new-tab --title "MoCKA-WORK"                           cmd /k "cd /d C:\Users\sirok\MoCKA" ^
; new-tab --title "MoCKA-WATCHER"   --tabColor "#1e5f3a" cmd /k "cd /d C:\Users\sirok\MoCKA && set "MOCKA_FIREBASE_KEY_PATH=A:\secrets\mocka-knowledge-gate.json" && python -X utf8 interface\mocka_watcher.py" ^
; new-tab --title "HEALTH-CHECK"    --tabColor "#5f5f00" cmd /k "cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python -X utf8 interface/health_check.py && pause" ^
; new-tab --title "BEE-DAILY"       --tabColor "#005f5f" cmd /k "cd /d C:\Users\sirok\MoCKA && timeout /t 5 /nobreak > nul && python -X utf8 structural/bee.py --daily && pause" ^
; new-tab --title "LIVING-ROOM"     --tabColor "#3a1e5f" cmd /k "cd /d C:\Users\sirok\MoCKA && python -X utf8 living_room/hub.py"

REM ============================================================
REM [PHASE 3.5] Post-launch duplicate-PID self-check (Phase5-2.2)
REM ============================================================
timeout /t 8 /nobreak > nul
echo [PHASE 3.5] Verifying no duplicate PIDs on ports 5000/5002/5679...
powershell -NoProfile -Command "$ports=5000,5002,5679; $dup=$false; foreach($p in $ports){ $owners = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if(($owners | Measure-Object).Count -gt 1){ Write-Host \"[WARN] Port $p has multiple listeners: $($owners -join ',')\"; $dup=$true } }; if(-not $dup){ Write-Host '[OK] No duplicate PIDs detected on 5000/5002/5679' }"

REM ============================================================
REM [PHASE 4] Browser
REM ============================================================
timeout /t 2 /nobreak > nul
start "" http://localhost:5000

REM ============================================================
REM [PHASE 5] TIC Risk Dashboard
REM ============================================================
start /B "" cmd /c "cd /d C:\Users\sirok\MoCKA && python -X utf8 interface\risk_interpreter.py"