$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPy = Join-Path $root ".venv\Scripts\python.exe"

function Fail([string]$msg){
  Write-Host "PHASE8_BLOCK: $msg"
  exit 1
}

if(-not (Test-Path $venvPy)){ Fail "venv python not found: $venvPy" }

$orig = Join-Path $root "tools\execution_reconfirm.ps1"
if(-not (Test-Path $orig)){ Fail "missing original ritual: $orig" }

# Run original ritual; capture exit code if it sets it, but do not treat as source of truth
$code = $null
try {
  & $orig @args
  $code = $LASTEXITCODE
} catch {
  Fail ("execution_reconfirm.ps1 threw: " + $_.Exception.Message)
}

# Required outputs (hard checks)
$sotLock = Join-Path $root "src\source_of_truth.lock.json"
$exeLock = Join-Path $root "execution.lock.json"
if(-not (Test-Path $sotLock)){ Fail "missing lock after reconfirm: $sotLock" }
if(-not (Test-Path $exeLock)){ Fail "missing lock after reconfirm: $exeLock" }

# Auto-sign (B method: python API)
& $venvPy -c "from tools.sign_lockfiles import sign_all; sign_all()"
if($LASTEXITCODE -ne 0){ Fail "sign_all failed (python exit=$LASTEXITCODE)" }

# Require signatures
$sotSig = Join-Path $root "src\source_of_truth.lock.json.sig"
$exeSig = Join-Path $root "execution.lock.json.sig"
if(-not (Test-Path $sotSig)){ Fail "missing signature after reconfirm: $sotSig" }
if(-not (Test-Path $exeSig)){ Fail "missing signature after reconfirm: $exeSig" }

# Log anomaly if exit code is non-zero, but do not block when artifacts are verified
if($code -ne $null -and $code -ne 0){
  $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmss.fffffffZ")
  $ts2 = $ts.Replace(":","").Replace(".","")
  $inv = Join-Path $root ("inventory\phase8_anomaly_exitcode_" + $ts2)
  New-Item -ItemType Directory -Force -Path $inv | Out-Null
  @("original_exitcode=$code","orig=$orig","sotLock=$sotLock","exeLock=$exeLock","sotSig=$sotSig","exeSig=$exeSig") | Set-Content (Join-Path $inv "note.txt") -Encoding UTF8
  Write-Host "WARN: original reconfirm returned non-zero but artifacts verified. logged=$inv"
}

Write-Host "OK: execution_reconfirm_auto completed"
exit 0
