param(
  [string]$Root="C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference="Stop"

$mapPath = Join-Path $Root "_canon\docs\RESEARCH_MAP.md"
$registry = Join-Path $Root "MoCKA\tools\research_experiments.json"

if(-not (Test-Path $mapPath)){ throw "RESEARCH_MAP_NOT_FOUND: $mapPath" }
if(-not (Test-Path $registry)){ throw "REGISTRY_NOT_FOUND: $registry" }

$map = Get-Content -LiteralPath $mapPath -Raw -Encoding UTF8
$j = Get-Content -LiteralPath $registry -Raw -Encoding UTF8 | ConvertFrom-Json

foreach($exp in $j.experiments){

  $id = $exp.id

  if($map -notmatch [regex]::Escape($id)){
    Write-Host "FAIL: MAP_MISSING_EXPERIMENT:" $id
    exit 1
  }

  Write-Host "OK_MAP_LINK:" $id
}

Write-Host "RESEARCH_MAP_REGISTRY_CHECK: OK"
