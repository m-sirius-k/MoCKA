# update_claude_settings.ps1
# ngrok URL を mocka.nsjp.org に切り替える
# VPS と SSL が設定完了してから実行すること

$SETTINGS = "$env:USERPROFILE\.claude\settings.json"
$NEW_URL   = "https://mocka.nsjp.org/mcp"

$json = Get-Content $SETTINGS -Raw | ConvertFrom-Json
$json.mcpServers.mocka.url = $NEW_URL
$json | ConvertTo-Json -Depth 10 | Set-Content $SETTINGS -Encoding UTF8

Write-Host "[done] Claude MCP URL → $NEW_URL"
Write-Host "Claude Code を再起動して接続を確認してください"
