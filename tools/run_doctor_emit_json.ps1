param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$doctor = Join-Path $Root "mocka_doctor.ps1"
if(-not (Test-Path -LiteralPath $doctor)){
  throw "DOCTOR_NOT_FOUND: $doctor"
}

$out = & powershell -NoProfile -ExecutionPolicy Bypass -File $doctor 2>&1 | Out-String

function PickText {
  param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$Text
  )
  $pattern = "(?m)^\s*" + [regex]::Escape($Name) + ":\s*(.+)\s*$"
  $m = [regex]::Match($Text, $pattern)
  if($m.Success){ return $m.Groups[1].Value.Trim() }
  return $null
}

$ts = Get-Date
$tsId = $ts.ToString("yyyyMMdd_HHmmss")
$tsLocal = $ts.ToString("yyyy-MM-ddTHH:mm:ssK")

$dir = "C:\Users\sirok\mocka-ecosystem\MoCKA\artifacts\doctor_runs"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$record = [ordered]@{
  ts_id = $tsId
  ts_local = $tsLocal
  root = $Root
  summary = [ordered]@{
    missing_repos   = PickText -Name "MISSING REPOS"   -Text $out
    dirty_git_repos = PickText -Name "DIRTY GIT REPOS" -Text $out
    mermaid_issues  = PickText -Name "MERMAID ISSUES"  -Text $out
    broken_links    = PickText -Name "BROKEN LINKS"    -Text $out
  }
  raw = $out
}

$pathStamped = Join-Path $dir ("doctor_run_" + $tsId + ".json")
$pathLatest  = Join-Path $dir "doctor_run_latest.json"

$json = ($record | ConvertTo-Json -Depth 6)

# write stamped + latest
$json | Set-Content -LiteralPath $pathStamped -Encoding UTF8
$json | Set-Content -LiteralPath $pathLatest  -Encoding UTF8

# sha256 for stamped json
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $pathStamped).Hash.ToLower()
$shaPath = Join-Path $dir ("doctor_run_" + $tsId + ".sha256.txt")
($hash + "  " + (Split-Path -Leaf $pathStamped) + "`n") | Set-Content -LiteralPath $shaPath -Encoding UTF8

Write-Host "DOCTOR_JSON_SAVED_LATEST:" $pathLatest
Write-Host "DOCTOR_JSON_SAVED_STAMPED:" $pathStamped
Write-Host "DOCTOR_JSON_SHA256:" $shaPath
Write-Host "DOCTOR_EMIT_JSON: OK"
