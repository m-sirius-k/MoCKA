# singleton_enforce.ps1
#
# MoCKA process singleton enforcement, shared by MoCKA-START.bat and restart_mocka.bat.
#
# Background: Name='python.exe' (Win32_Process -Filter) and `taskkill /IM python.exe`
# silently match zero processes on this machine because the real image name is
# python3.13.exe, not python.exe. Both scripts carried this bug independently, which
# let stale background processes (sync_watch.py etc.) survive restarts and produce
# duplicate commits/pushes against origin/main (2026-07-02 MoCKA-STARTUP-DUPLICATION).
#
# Fix: CommandLine regex match via Get-CimInstance Win32_Process (no -Filter on Name)
# is the sole kill criterion, so it never depends on the interpreter's image name or
# install location. Resolved python path is diagnostic only and never gates the kill.
#
# Self-match guard: this script's own invocation (e.g. -Pattern "python") necessarily
# contains the pattern text in its own CommandLine. Verified by testing: an early
# version killed its own process and its immediate parent shell. Self and parent PID
# are excluded from the candidate pool before the CommandLine match is applied.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File singleton_enforce.ps1 -Pattern "sync_watch\.py|ping_generator\.py"
#   powershell -NoProfile -ExecutionPolicy Bypass -File singleton_enforce.ps1 -Pattern "python"

param(
    [Parameter(Mandatory = $true)]
    [string]$Pattern
)

if ($env:VIRTUAL_ENV) {
    $resolvedPython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
} else {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    $resolvedPython = if ($cmd) { $cmd.Source } else { "(not found)" }
}
Write-Host "[singleton_enforce] resolved python (diagnostic only, not used for matching): $resolvedPython"

$currentPid = $PID
$parentPid = (Get-CimInstance Win32_Process -Filter "ProcessId=$currentPid" -ErrorAction SilentlyContinue).ParentProcessId

$targets = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessId -ne $currentPid -and $_.ProcessId -ne $parentPid -and
    $_.CommandLine -and ($_.CommandLine -match $Pattern)
}

if (-not $targets) {
    Write-Host "[singleton_enforce] no matching processes for pattern: $Pattern"
    exit 0
}

foreach ($proc in $targets) {
    Write-Host "[singleton_enforce] stopping PID $($proc.ProcessId): $($proc.CommandLine)"
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}
