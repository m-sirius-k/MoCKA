# startup_guard.ps1
#
# MoCKA pre-launch duplicate-instance guard, called by MoCKA-START.bat.
#
# Background: an earlier version embedded this check as a caret(^)-continued
# multi-line `powershell -Command` block directly inside MoCKA-START.bat.
# That nesting style (multi-line continuation inside a double-quoted string
# passed to a nested powershell -Command) proved unstable depending on the
# calling shell context, surfacing as native PowerShell parse errors instead
# of a clean batch abort. Splitting it into a standalone script invoked via
# a single `-File` call removes the caret-continuation entirely, so this
# class of interpretation error cannot occur (2026-07-02).
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File startup_guard.ps1

$pattern = 'ping_generator\.py|sync_watch\.py|tech_watcher\.py|risk_scorer\.py|essence_auto_updater\.py|check_utf8_mandate\.py|app\.py|mocka_mcp_server\.py|gateway\.py|living_room[\\/]hub\.py'

$running = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match $pattern }

if ($running) {
    Write-Host "=============================================="
    Write-Host "[ABORT] MoCKA already running:"
    $running | ForEach-Object { Write-Host "  PID $($_.ProcessId): $($_.CommandLine)" }
    Write-Host "=============================================="
    exit 1
}

exit 0
