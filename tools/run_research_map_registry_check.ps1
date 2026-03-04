param(
  [string]$Root="C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference="Stop"

$mapA = Join-Path $Root "_canon\docs\RESEARCH_MAP.md"
$mapB = Join-Path $Root "MoCKA\canon\RESEARCH_MAP.md"
$registry = Join-Path $Root "MoCKA\tools\research_experiments.json"

$mapPath = $null
if(Test-Path -LiteralPath $mapA){ $mapPath = $mapA }
elseif(Test-Path -LiteralPath $mapB){ $mapPath = $mapB }
else{ throw "RESEARCH_MAP_NOT_FOUND: $mapA OR $mapB" }

if(-not (Test-Path -LiteralPath $registry)){ throw "REGISTRY_NOT_FOUND: $registry" }

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
