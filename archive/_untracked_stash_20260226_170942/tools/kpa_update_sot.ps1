param(
  [Parameter(Mandatory=$true)][string]$TargetPath,
  [Parameter(Mandatory=$true)][string]$NewContentPath
)

$ErrorActionPreference = "Stop"

function Sha256([string]$p){
  (Get-FileHash -Algorithm SHA256 -Path $p).Hash.ToUpperInvariant()
}

function Require([bool]$cond, [string]$msg){
  if(-not $cond){ throw $msg }
}

$root = (Get-Location).Path
$invDir = Join-Path $root "inventory"

Require (Test-Path $invDir) "KPA_FAIL inventory missing"

$sotTxt = Join-Path $root "src\source_of_truth.lock"
$sotJson = Join-Path $root "src\source_of_truth.lock.json"
$execJson = Join-Path $root "execution.lock.json"

Require (Test-Path $sotTxt) "KPA_FAIL source_of_truth.lock missing"
Require (Test-Path $TargetPath) "KPA_FAIL target missing"
Require (Test-Path $NewContentPath) "KPA_FAIL new content missing"

$ts = (Get-Date).ToUniversalTime().ToString("o")
$tag = $ts.Replace(":","").Replace("-","").Replace(".","")

$session = Join-Path $invDir ("phase7_sot_update_" + $tag)
New-Item -ItemType Directory -Force -Path $session | Out-Null

$targetFull = (Resolve-Path $TargetPath).Path
$newFull = (Resolve-Path $NewContentPath).Path

$beforeHash = Sha256 $targetFull
Copy-Item -Force $targetFull (Join-Path $session "target.before")

Copy-Item -Force $newFull $targetFull

$afterHash = Sha256 $targetFull

# update text lock
$lines = Get-Content $sotTxt
$out = @()

foreach($line in $lines){
  if($line -match "SHA256=([0-9A-Fa-f]{64})" -and $line -match (Split-Path $targetFull -Leaf)){
    $prefix = ($line -split "SHA256=",2)[0]
    $out += ($prefix + "SHA256=" + $afterHash)
  } else {
    $out += $line
  }
}

$out | Out-File -Encoding utf8 $sotTxt -Force

# update JSON lock if exists
if(Test-Path $sotJson){
  $j = Get-Content $sotJson -Raw | ConvertFrom-Json
  $j.files.(Split-Path $targetFull -Leaf) = $afterHash
  $j.locked_at = $ts
  $j | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 $sotJson -Force
}

# invalidate execution lock (Phase7.2 core)
if(Test-Path $execJson){
  Remove-Item -Force $execJson
}

"OK PHASE7.2_SOT_UPDATE session=$session"