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

function Fail($msg){
  Write-Host "FAIL:" $msg
  exit 1
}

# 1) Ecosystem integrity (doctor)
$doctor = Join-Path $Root "mocka_doctor.ps1"
if(-not (Test-Path -LiteralPath $doctor)){
  Fail "DOCTOR_NOT_FOUND: $doctor"
}

Write-Host "RUN:" $doctor
powershell -ExecutionPolicy Bypass -File $doctor

# 2) Per-repo checks
foreach($r in $repos){

  $repoPath = Join-Path $Root $r
  if(-not (Test-Path -LiteralPath $repoPath)){
    Fail "REPO_NOT_FOUND: $repoPath"
  }

  Set-Location $repoPath

  # 2.1 git clean
  $st = git status --porcelain
  if($st){
    Write-Host $st
    Fail "GIT_DIRTY: $r"
  }

  # 2.2 research map exists
  $rm = Join-Path $repoPath "RESEARCH_MAP.md"
  if(-not (Test-Path -LiteralPath $rm)){
    Fail "RESEARCH_MAP_MISSING: $rm"
  }

  # 2.3 experiments dir exists
  $expDir = Join-Path $repoPath "experiments"
  if(-not (Test-Path -LiteralPath $expDir)){
    Fail "EXPERIMENTS_DIR_MISSING: $expDir"
  }

  # 2.4 count experiments (md)
  $n = 0
  if(Test-Path -LiteralPath $expDir){
    $n = (Get-ChildItem -LiteralPath $expDir -Filter *.md -File -ErrorAction SilentlyContinue | Measure-Object).Count
  }

  Write-Host "OK:" $r "experiments=" $n
}

Write-Host "RESEARCH_RUN: OK"
