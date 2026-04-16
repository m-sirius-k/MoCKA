param(
  [Parameter(Mandatory=$true)][string]$TargetPath,
  [string]$NewContentPath = "",
  [string]$NewContentText = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPy = Join-Path $root ".venv\Scripts\python.exe"

function Fail([string]$msg){
  Write-Host "PHASE8_BLOCK: $msg"
  exit 1
}

if([string]::IsNullOrWhiteSpace($TargetPath)){ Fail "TargetPath is empty" }
if(-not (Test-Path $venvPy)){ Fail "venv python not found: $venvPy" }

# Resolve target under repo
$tp = (Resolve-Path (Join-Path $root $TargetPath) -ErrorAction SilentlyContinue)
if(-not $tp){ Fail "TargetPath not found under repo: $TargetPath" }
$tp = $tp.Path

# Enforce src/ only
$srcRoot = (Resolve-Path (Join-Path $root "src")).Path
if(-not ($tp.ToLower().StartsWith($srcRoot.ToLower()))){
  Fail "TargetPath must be under src/: $tp"
}

$orig = Join-Path $root "tools\kpa_update_sot.ps1"
if(-not (Test-Path $orig)){ Fail "missing original ritual: $orig" }

# Decide payload path:
# 1) NewContentPath (if provided)
# 2) NewContentText (if provided)
# 3) Clipboard (fallback)
$np = $null

if(-not [string]::IsNullOrWhiteSpace($NewContentPath)){
  $rp = (Resolve-Path (Join-Path $root $NewContentPath) -ErrorAction SilentlyContinue)
  if(-not $rp){ Fail "NewContentPath not found under repo: $NewContentPath" }
  $np = $rp.Path
} else {
  if([string]::IsNullOrWhiteSpace($NewContentText)){
    try { $NewContentText = (Get-Clipboard -Raw) } catch { Fail "NewContentText not provided and clipboard unavailable" }
  }
  if([string]::IsNullOrWhiteSpace($NewContentText)){ Fail "NewContentText is empty (and clipboard empty)" }

  $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmss.fffffffZ")
  $ts2 = $ts.Replace(":","").Replace(".","")
  $inv = Join-Path $root ("inventory\phase8_payload_" + $ts2)
  New-Item -ItemType Directory -Force -Path $inv | Out-Null
  $np = Join-Path $inv "payload.txt"
  $NewContentText | Set-Content -Path $np -Encoding UTF8
}

# Snapshot before
$beforeSot = Join-Path $root "src\source_of_truth.lock.json"
$beforeSotTime = if(Test-Path $beforeSot){ (Get-Item $beforeSot).LastWriteTimeUtc } else { [datetime]"1900-01-01" }

# Run original ritual (do NOT use $LASTEXITCODE)
try {
  & $orig -TargetPath $tp -NewContentPath $np
} catch {
  Fail ("kpa_update_sot.ps1 threw: " + $_.Exception.Message)
}

# Artifact checks (success criteria)
if(-not (Test-Path $beforeSot)){ Fail "missing after ritual: src\source_of_truth.lock.json" }
$afterSotTime = (Get-Item $beforeSot).LastWriteTimeUtc
if($afterSotTime -le $beforeSotTime){ Fail "source_of_truth.lock.json not updated (timestamp unchanged)" }

# By design: execution.lock.json should be removed to force reconfirm
$exeLock = Join-Path $root "execution.lock.json"
if(Test-Path $exeLock){ Fail "execution.lock.json still exists (should be removed by SOT update ritual)" }

# Auto-sign (B method: python API)
& $venvPy -c "from tools.sign_lockfiles import sign_all; sign_all()"
if($LASTEXITCODE -ne 0){ Fail "sign_all failed (python exit=$LASTEXITCODE)" }

# Require signature for SOT lock
$sotSig = Join-Path $root "src\source_of_truth.lock.json.sig"
if(-not (Test-Path $sotSig)){ Fail "missing signature after ritual: $sotSig" }

Write-Host "OK: kpa_update_sot_auto completed"
exit 0
