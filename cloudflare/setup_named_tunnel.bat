@echo off
chcp 65001 >nul
REM MoCKA Named Tunnel Setup (TODO_266)
REM Run this script ONCE as kimura-hakase to create the Named Tunnel
REM Requires: cloudflared installed + Cloudflare account with nsjp.org domain

echo [STEP 1] Login to Cloudflare (browser will open)
cloudflared tunnel login

echo [STEP 2] Create Named Tunnel "mocka-mcp"
cloudflared tunnel create mocka-mcp

echo [STEP 3] Route DNS (requires nsjp.org in Cloudflare)
cloudflared tunnel route dns mocka-mcp mcp.nsjp.org

echo [DONE] Named Tunnel created.
echo Fixed URL: https://mcp.nsjp.org
echo.
echo Next: Update C:\Users\sirok\.cloudflared\config.yml with TUNNEL_ID
echo Then: Add "cloudflared tunnel run mocka-mcp" to MoCKA-START.bat
pause
