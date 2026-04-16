param(
  [Parameter(Mandatory=$true)][string]$TargetPath,
  [Parameter(Mandatory=$true)][string]$NewContentPath
)

$ErrorActionPreference = "Stop"

function Sha256([string]$p){
  return (Get-FileHash -Algorithm SHA256 -Path $p).Hash
}

function Require([bool]$cond, [string]$msg){
  if(-not $cond){ throw $msg }
}

$root = (Get-Location).Path
$invDir = Join-Path $root "inventory"
Require (Test-Path $invDir) ("KPA_FAIL inventory missing: " + $invDir)

$execLock = Join-Path $root "execution.lock"
Require (Test-Path $execLock) ("KPA_FAIL execution.lock missing: " + $execLock)

$sotLock = Join-Path $root "src\source_of_truth.lock"
Require (Test-Path $sotLock) ("KPA_FAIL source_of_truth.lock missing: " + $sotLock)

Require (Test-Path $TargetPath) ("KPA_FAIL target missing: " + $TargetPath)
Require (Test-Path $NewContentPath) ("KPA_FAIL new content missing: " + $NewContentPath)

# === 正本保護チェック ===
$lockLines = Get-Content $sotLock
$protected = @()

foreach($line in $lockLines){
  if($line -match "source_of_truth"){
    $name = ($line -split ":")[1] -split "@"
    $protected += $name[0].Trim()
  }
}

$targetName = (Split-Path $TargetPath -Leaf)

if($protected -contains $targetName){
  throw ("KPA_PROTECTED_FILE: " + $targetName + " is protected by source_of_truth.lock")
}

$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$session = Join-Path $invDir ("phase6_enforcer_" + $ts)
New-Item -ItemType Directory -Force -Path $session | Out-Null

$targetFull = (Resolve-Path $TargetPath).Path
$newFull = (Resolve-Path $NewContentPath).Path

$bak = Join-Path $session "target.before"
Copy-Item -Force $targetFull $bak

$beforeHash = Sha256 $bak
$beforeLen  = (Get-Item $bak).Length

Copy-Item -Force $newFull (Join-Path $session "new_content.used")

Copy-Item -Force $newFull $targetFull

$afterHash = Sha256 $targetFull
$afterLen  = (Get-Item $targetFull).Length

$diffPath = Join-Path $session "diff.patch"
try {
  git diff --no-index -- "$bak" "$targetFull" | Out-File -Encoding utf8 $diffPath
} catch {
  ("DIFF_UNAVAILABLE: " + $_.Exception.Message) | Out-File -Encoding utf8 $diffPath
}

@(
  "ts_utc=$ts"
  "target=$targetFull"
  "new_content=$newFull"
  "before_sha256=$beforeHash"
  "after_sha256=$afterHash"
  "before_bytes=$beforeLen"
  "after_bytes=$afterLen"
  "diff=$diffPath"
) | Out-File -Encoding utf8 (Join-Path $session "enforcer_record.txt")

Require (Test-Path $bak) ("KPA_FAIL backup missing after write")
Require ($afterHash -ne "") ("KPA_FAIL after hash empty")

"OK KPA_EDIT session=" + $session
