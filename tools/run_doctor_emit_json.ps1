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

# parse summary fields (best-effort, strict keys)
function PickInt($name, $text){
  $m = [regex]::Match($text, "(?m)^\s*$name:\s*(\d+)\s*$")
  if($m.Success){ return [int]$m.Groups[1].Value }
  return $null
}

function PickText($name, $text){
  $m = [regex]::Match($text, "(?m)^\s*$name:\s*(.+)\s*$")
  if($m.Success){ return $m.Groups[1].Value.Trim() }
  return $null
}

$record = [ordered]@{
  ts_local = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
  root = $Root
  summary = [ordered]@{
    missing_repos = PickText "MISSING REPOS" $out
    dirty_git_repos = PickText "DIRTY GIT REPOS" $out
    mermaid_issues = PickText "MERMAID ISSUES" $out
    broken_links = PickText "BROKEN LINKS" $out
  }
  raw = $out
}

$pathLatest = "C:\Users\sirok\mocka-ecosystem\MoCKA\artifacts\doctor_runs\doctor_run_latest.json"
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $pathLatest -Encoding UTF8

Write-Host "DOCTOR_JSON_SAVED:" $pathLatest
Write-Host "DOCTOR_EMIT_JSON: OK"
