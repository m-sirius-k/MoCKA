[CmdletBinding()]
param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem",
  [string]$Registry = "C:\Users\sirok\mocka-ecosystem\MoCKA\tools\research_experiments.json"
)

$ErrorActionPreference = "Stop"

function Fail([string]$msg){
  Write-Host "FAIL:" $msg
  exit 1
}

function Run-CommandCapture {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [string[]]$Args = @()
  )
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = "powershell"
  $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$FilePath`" " + ($Args -join " ")
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError  = $true
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true

  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  [void]$p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()

  return @{
    code = $p.ExitCode
    out  = $stdout
    err  = $stderr
  }
}

# 0) load registry
if(-not (Test-Path -LiteralPath $Registry)){
  Fail "REGISTRY_NOT_FOUND: $Registry"
}
$cfg = Get-Content -LiteralPath $Registry -Raw -Encoding UTF8 | ConvertFrom-Json

# 1) per-repo structural checks
$repos = @(
  "MoCKA",
  "MoCKA-KNOWLEDGE-GATE",
  "mocka-civilization",
  "mocka-transparency",
  "mocka-external-brain",
  "mocka-core-private"
)

foreach($r in $repos){
  $repoPath = Join-Path $Root $r
  if(-not (Test-Path -LiteralPath $repoPath)){
    Fail "REPO_NOT_FOUND: $repoPath"
  }
  Set-Location $repoPath

  $st = git status --porcelain
  if($st){
    Write-Host $st
    Fail "GIT_DIRTY: $r"
  }

  $rm = Join-Path $repoPath "RESEARCH_MAP.md"
  if(-not (Test-Path -LiteralPath $rm)){
    Fail "RESEARCH_MAP_MISSING: $rm"
  }

  $expDir = Join-Path $repoPath "experiments"
  if(-not (Test-Path -LiteralPath $expDir)){
    Fail "EXPERIMENTS_DIR_MISSING: $expDir"
  }
}

# 2) execute experiments from registry
foreach($e in $cfg.experiments){
  $id = [string]$e.id
  $kind = [string]$e.kind
  $script = [string]$e.script

  Write-Host "RUN_EXPERIMENT:" $id

  if($kind -ne "ps1"){
    Fail "UNSUPPORTED_KIND: $kind id=$id"
  }
  if(-not (Test-Path -LiteralPath $script)){
    Fail "SCRIPT_NOT_FOUND: $script id=$id"
  }

  $res = Run-CommandCapture -FilePath $script -Args @("-Root", "`"$Root`"")
  if($res.code -ne 0){
    Write-Host $res.out
    Write-Host $res.err
    Fail "EXPERIMENT_FAILED: id=$id exit=$($res.code)"
  }

  $out = $res.out + "`n" + $res.err
  foreach($needle in $e.expect_contains){
    if($out -notmatch [regex]::Escape([string]$needle)){
      Write-Host $out
      Fail "EXPECT_MISSING: id=$id missing=`"$needle`""
    }
  }

  Write-Host "OK_EXPERIMENT:" $id
}

Write-Host "RESEARCH_RUN: OK"
