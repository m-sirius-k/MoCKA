param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$doctor = Join-Path $Root "mocka_doctor.ps1"
if(-not (Test-Path -LiteralPath $doctor)){
  throw "DOCTOR_NOT_FOUND: $doctor"
}

# capture doctor output
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

$record = [ordered]@{
  ts_local = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  root = $Root
  summary = [ordered]@{
    missing_repos   = PickText -Name "MISSING REPOS"   -Text $out
    dirty_git_repos = PickText -Name "DIRTY GIT REPOS" -Text $out
    mermaid_issues  = PickText -Name "MERMAID ISSUES"  -Text $out
    broken_links    = PickText -Name "BROKEN LINKS"    -Text $out
  }
  raw = $out
}

$dir = "C:\Users\sirok\mocka-ecosystem\MoCKA\artifacts\doctor_runs"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$pathLatest = Join-Path $dir "doctor_run_latest.json"
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $pathLatest -Encoding UTF8

Write-Host "DOCTOR_JSON_SAVED:" $pathLatest
Write-Host "DOCTOR_EMIT_JSON: OK"
