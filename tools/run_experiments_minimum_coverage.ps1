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

function Fail([string]$msg){
  Write-Host "FAIL:" $msg
  exit 1
}

foreach($r in $repos){

  $repoPath = Join-Path $Root $r
  $expDir = Join-Path $repoPath "experiments"

  if(-not (Test-Path -LiteralPath $expDir)){
    Fail "EXPERIMENTS_DIR_NOT_FOUND: $expDir"
  }

  $count = (Get-ChildItem -LiteralPath $expDir -Filter *.md -File -ErrorAction SilentlyContinue | Measure-Object).Count
  if($count -lt 1){
    Fail "EXPERIMENTS_EMPTY: repo=$r dir=$expDir"
  }

  Write-Host "OK_EXPERIMENTS_COVERAGE:" $r "count=" $count
}

Write-Host "EXPERIMENTS_MINIMUM_COVERAGE: OK"
