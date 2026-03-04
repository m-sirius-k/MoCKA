param(
  [string]$Root="C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference="Stop"

$repos=@(
"MoCKA",
"MoCKA-KNOWLEDGE-GATE",
"mocka-civilization",
"mocka-transparency",
"mocka-external-brain",
"mocka-core-private"
)

foreach($r in $repos){

  $readme = Join-Path (Join-Path $Root $r) "README.md"

  if(-not (Test-Path -LiteralPath $readme)){
    Write-Host "FAIL: README_NOT_FOUND:" $r
    exit 1
  }

  $txt = Get-Content -LiteralPath $readme -Raw -Encoding UTF8

  # minimal presence check: must include the word "Research"
  if($txt -notmatch "(?i)research"){
    Write-Host "FAIL: RESEARCH_ENTRY_MISSING:" $r
    exit 1
  }

  Write-Host "OK_RESEARCH_ENTRY:" $r
}

Write-Host "README_RESEARCH_ENTRY_CHECK: OK"
