param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$repos = @(
"MoCKA",
"MoCKA-KNOWLEDGE-GATE",
"mocka-civilization",
"mocka-transparency",
"mocka-external-brain",
"mocka-core-private"
)

function Assert([bool]$cond, [string]$msg){
  if(-not $cond){ throw $msg }
}

foreach($r in $repos){

  $repoPath = Join-Path $Root $r
  Assert (Test-Path -LiteralPath $repoPath) ("REPO_NOT_FOUND: " + $repoPath)

  $readme = Join-Path $repoPath "README.md"
  Assert (Test-Path -LiteralPath $readme) ("README_NOT_FOUND: " + $readme)

  $rm = Join-Path $repoPath "RESEARCH_MAP.md"
  Assert (Test-Path -LiteralPath $rm) ("RESEARCH_MAP_NOT_FOUND: " + $rm)

  $exp = Join-Path $repoPath "experiments"
  Assert (Test-Path -LiteralPath $exp) ("EXPERIMENTS_DIR_NOT_FOUND: " + $exp)

  $txt = Get-Content -LiteralPath $readme -Raw -Encoding UTF8
  Assert ($txt -match "(?m)^\s*##\s+Research Map\s*$") ("README_MISSING_RESEARCH_MAP_HEADING: " + $readme)
  Assert ($txt -match "(?m)^\s*See:\s*RESEARCH_MAP\.md\s*$") ("README_MISSING_RESEARCH_MAP_LINKLINE: " + $readme)

  Write-Host "OK_REPO_ENTRYPOINTS:" $r
}

Write-Host "ENTRYPOINTS_CHECK: OK"
