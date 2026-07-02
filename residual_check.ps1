# residual_check.ps1
#
# Post-kill residual-process warning, called by restart_mocka.bat after
# singleton_enforce.ps1. Warn-only: never aborts. MoCKA-START.bat's own
# startup_guard.ps1 is the final gate if a process failed to stop in time.
#
# Split out of restart_mocka.bat for the same reason as startup_guard.ps1:
# a caret(^)-continued multi-line `powershell -Command` block nested inside
# a batch file proved unstable depending on the calling shell context. A
# standalone script invoked via a single `-File` call removes the caret
# continuation entirely (2026-07-02).
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File residual_check.ps1

$pattern = 'ping_generator\.py|sync_watch\.py|tech_watcher\.py|risk_scorer\.py|essence_auto_updater\.py|check_utf8_mandate\.py|app\.py|mocka_mcp_server\.py|gateway\.py|living_room[\\/]hub\.py'

$still = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match $pattern }

if ($still) {
    Write-Host "[WARN] some processes did not stop:"
    $still | ForEach-Object { Write-Host "  PID $($_.ProcessId): $($_.CommandLine)" }
}
