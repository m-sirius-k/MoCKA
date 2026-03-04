param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$allowed = @(
"Institutional Memory",
"Verification",
"Transparency",
"Boundary"
)

$expect = @{
  "MoCKA"               = "Boundary"
  "MoCKA-KNOWLEDGE-GATE"= "Institutional Memory"
  "mocka-civilization"  = "Institutional Memory"
  "mocka-transparency"  = "Transparency"
  "mocka-external-brain"= "Verification"
  "mocka-core-private"  = "Boundary"
}

function Fail([string]$msg){
  Write-Host "FAIL:" $msg
  exit 1
}

foreach($r in $expect.Keys){

  $readme = Join-Path (Join-Path $Root $r) "README.md"
  if(-not (Test-Path -LiteralPath $readme)){
    Fail "README_NOT_FOUND: $readme"
  }

  $txt = Get-Content -LiteralPath $readme -Raw -Encoding UTF8

  if($txt -notmatch "(?m)^\s*Primary Role:\s*(.+)\s*$"){
    Fail "PRIMARY_ROLE_LINE_MISSING: $readme"
  }

  $role = $Matches[1].Trim()

  if($allowed -notcontains $role){
    Fail "ROLE_NOT_ALLOWED: repo=$r role=$role"
  }

  $exp = $expect[$r]
  if($role -ne $exp){
    Fail "ROLE_MISMATCH: repo=$r expected=$exp got=$role"
  }

  Write-Host "OK_ROLE:" $r "=" $role
}

Write-Host "README_ROLE_VOCAB_CHECK: OK"
