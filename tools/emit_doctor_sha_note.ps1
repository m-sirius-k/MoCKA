param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$dir = Join-Path $Root "MoCKA\artifacts\doctor_runs"
if(-not (Test-Path -LiteralPath $dir)){
  throw "DOCTOR_RUN_DIR_NOT_FOUND: $dir"
}

$latestSha = Get-ChildItem -LiteralPath $dir -Filter "doctor_run_*.sha256.txt" -File |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if(-not $latestSha){
  throw "NO_SHA256_FOUND in $dir"
}

$sha = Get-Content -LiteralPath $latestSha.FullName -Raw -Encoding UTF8

# infer json file name from sha file
$jsonLeaf = ($latestSha.Name -replace "\.sha256\.txt$",".json")
$ts = (Get-Date $latestSha.LastWriteTime).ToString("yyyy-MM-dd HH:mm:ss")

$noteTitle = "MoCKA Doctor Artifact Hash Log v1"
$body = @"
# MoCKA Doctor Artifact Hash Log v1

## Timestamp
$ts (local)

## Artifact
MoCKA\artifacts\doctor_runs\$jsonLeaf

## SHA256
$sha
"@

$noteTool = Join-Path $Root "tools\note_args.ps1"
if(-not (Test-Path -LiteralPath $noteTool)){
  throw "NOTE_TOOL_NOT_FOUND: $noteTool"
}

& $noteTool -Title $noteTitle -Mode upsert -Body $body
Write-Host "NOTE_UPSERT_OK:" $noteTitle
