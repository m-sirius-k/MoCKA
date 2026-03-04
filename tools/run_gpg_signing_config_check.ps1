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
  if(-not (Test-Path -LiteralPath $repoPath)){
    Fail "REPO_NOT_FOUND: $repoPath"
  }

  Set-Location $repoPath

  $gpgsign = (git config --local --get commit.gpgsign)
  $signkey = (git config --local --get user.signingkey)
  $gpgprog = (git config --local --get gpg.program)

  if([string]::IsNullOrWhiteSpace($gpgsign)){ Fail "MISSING: commit.gpgsign repo=$r" }
  if($gpgsign.Trim().ToLower() -ne "true"){ Fail "INVALID: commit.gpgsign repo=$r value=$gpgsign" }

  if([string]::IsNullOrWhiteSpace($signkey)){ Fail "MISSING: user.signingkey repo=$r" }
  if([string]::IsNullOrWhiteSpace($gpgprog)){ Fail "MISSING: gpg.program repo=$r" }

  Write-Host "OK_GPG_SIGNING_CONFIG:" $r
}

Write-Host "GPG_SIGNING_CONFIG_CHECK: OK"
