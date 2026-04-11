@echo off
python C:\Users\sirok\MoCKA\interface\ping_generator.py
timeout /t 2 /nobreak > nul
echo [MoCKA] Starting...
start "" "C:\Users\sirok\AppData\Local\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9222
timeout /t 3 /nobreak > nul
wt -w 0 new-tab --title "MoCKA-APP" --tabColor "#005700" cmd /k "cd /d C:\Users\sirok\MoCKA && python app.py" ; new-tab --title "MoCKA-MCP" --tabColor "#5f1e3a" cmd /k "cd /d C:\Users\sirok\MoCKA && python mocka_mcp_server.py" ; new-tab --title "MoCKA-NGROK" --tabColor "#3a1e5f" cmd /k "ngrok http 5002" ; new-tab --title "MoCKA-WORK" cmd /k "cd /d C:\Users\sirok\MoCKA"
timeout /t 4 /nobreak > nul
start "" http://localhost:5000
